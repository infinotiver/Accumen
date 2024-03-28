import discord
import utils.functions as funcs
import datetime
import motor.motor_asyncio
import nest_asyncio
import os
import discord.utils
from dotenv import load_dotenv

os.chdir("..")
load_dotenv()
nest_asyncio.apply()

mongo_url = os.environ["mongodb"]

cluster = motor.motor_asyncio.AsyncIOMotorClient(mongo_url)
queries_col = cluster["accumen"]["queries"]
incoming = cluster["accumen"]["incoming"]
system = cluster["accumen"]["system"]


class developer_controls(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Dev Stats",
        style=discord.ButtonStyle.grey,
        custom_id="stats",
        emoji="📰",
    )
    async def stats(self, interaction: discord.Interaction, button: discord.ui.Button):
        results = await system.find_one({"_id": "commands_usage"})
        count = str(results["count"])
        system_latency = round(interaction.client.latency * 1000)
        embed = funcs.dembed(
            title="Statistics",
            description=f"**Total Command Requests:** {count}\n**Total Queries:** "
            + str(await queries_col.count_documents({})),
        )
        embed.set_thumbnail(url=interaction.client.user.avatar.url)
        embed.add_field(name="Ping", value=f"{system_latency} ms", inline=False)
        embed.add_field(
            name="Servers", value=f"{len(interaction.client.guilds)}", inline=True
        )
        embed.add_field(
            name="Users", value=f"{len(interaction.client.users)}", inline=True
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)


class answer_control_view(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Close Query",
        style=discord.ButtonStyle.danger,
        custom_id="persistent_view:close_query",
        emoji="🔒",
    )
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        query_id = self.message.embeds[0].description.split("\n")[3]
        query = await queries_col.find_one({"id": query_id})
        query["closed"] = True
        await queries_col.replace_one({"id": query_id}, query)
        await interaction.response.send_message("Query Closed", ephemeral=True)


# for assist.py --- User control panel (cmd = new)
class Qrscontrol(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Add an Answer",
        style=discord.ButtonStyle.success,
        custom_id="persistent_view:answer",
        emoji="✒",
    )
    async def ans(self, interaction: discord.Interaction, button: discord.ui.Button):

        query_id = self.message.embeds[0].description.split("\n")[0].split("**")[1]

        await interaction.response.send_message(
            f"Use command\n**</query answer:1085572802976952340> id {query_id}**",
            ephemeral=True,
        )

    @discord.ui.button(
        label="Upvote",
        style=discord.ButtonStyle.blurple,
        custom_id="persistent_view:vote",
        emoji="🔼",
    )
    async def vote(self, interaction: discord.Interaction, button: discord.ui.Button):
        query_id = self.message.embeds[0].description.split("\n")[0].split("**")[1]
        query = await queries_col.find_one({"id": query_id})
        voted_users = query.get("voted_users", [])

        if interaction.user.id in voted_users:
            query["votes"] -= 1
            voted_users.remove(interaction.user.id)
            await interaction.response.send_message(
                embed=funcs.dembed(description="Removed vote"), ephemeral=True
            )
        else:
            query["votes"] += 1
            voted_users.append(interaction.user.id)
            await interaction.response.send_message(
                embed=funcs.dembed(description="Added vote"), ephemeral=True
            )

        await queries_col.replace_one({"id": query_id}, query)

        for data in query.get("messages", []):
            try:
                guild_id = data.get("guild")
                guild = interaction.client.get_guild(int(guild_id))
                if guild is None:
                    continue

                channel_id = int(data.get("channel"))
                channel = guild.get_channel(channel_id)
                if channel is None:
                    continue

                msg = await channel.fetch_message(data.get("msg"))
                embed = msg.embeds[0]
                embed.set_field_at(0, name="Votes", value=str(query["votes"]))
                await msg.edit(embed=embed)

            except Exception as e:
                print(f"An error occurred while updating messages: {e}")

    @discord.ui.button(
        label="Report WIP",
        style=discord.ButtonStyle.red,
        custom_id="persistent_view:report",
        disabled=True,
        emoji="🛑",
    )
    async def report(self, interaction: discord.Interaction, button: discord.ui.Button):
        msg_id = interaction.message.id
        query = await queries_col.find_one(
            {"messages": {"$elemMatch": {"msg": msg_id}}}
        )
        query_id = query["id"]
        title = query["title"]
        description = query["description"]
        difficulty = query["difficulty"]
        user = query["user_id"]
        upvote_count = query["votes"]
        category = query["category"]
        embed = discord.Embed(
            title=f"**{title}**", description=description, color=funcs.theme
        )
        author_string = f"{user} ∙ {difficulty}"
        embed.set_footer(text=author_string)
        embed.set_author(name=interaction.user, icon_url=interaction.user.avatar.url)
        embed.add_field(name="Upvote", value=upvote_count)
        embed.add_field(name="Category", value=f"`{category}`")
        await interaction.client.get_channel(979345665081610271).send(
            f" {interaction.user.mention} Reported the following query", embed=embed
        )
        await interaction.response.send_message("Sent the report to the bot moderators")
