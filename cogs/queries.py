"""
TODO
  - Add Dynamic views
  - Add points and levelling system
"""

import discord
from discord.ext import commands, tasks
from discord import app_commands
import os
import utils.functions as funcs
from utils.functions import dembed, theme, divider
from discord.utils import format_dt
import motor.motor_asyncio
import nest_asyncio
import typing
from reactionmenu import ViewMenu, ViewButton
import utils.buttons as assetsb
import datetime

nest_asyncio.apply()

mongo_url = os.environ["mongodb"]

cluster = motor.motor_asyncio.AsyncIOMotorClient(mongo_url)
queries_col = cluster["accumen"]["queries"]
incoming = cluster["accumen"]["incoming"]


def delete_everything():
    queries_col.delete_many({})
    print("Deleted Everything")


# delete_everything()
SUBJECTS = {
    "Languages": "language",
    "Mathematics": "mathematics",
    "Biology": "biology",
    "Chemistry": "chemistry",
    "Physics": "physics",
    "History": "history",
    "Geography": "geography",
    "Computer Science": "computer_science",
    "Fine Arts": "fine_arts",
    "Economics": "economics",
    "Health Science": "health_science",
    "Law": "law",
    "Media Studies": "media_studies",
    "Other": "other",
}
EDUCATION_LEVELS = {
    "Primary School": "1",
    "Middle School": "2",
    "High School": "3",
    "Undergraduate": "4",
    "Postgraduate": "5",
    "Doctorate": "6",
}
Status = {"Open": "False", "Closed": "True"}
subject_choices = [
    app_commands.Choice(name=name, value=value) for name, value in SUBJECTS.items()
]
education_level_choices = [
    app_commands.Choice(name=name, value=value)
    for name, value in EDUCATION_LEVELS.items()
]
status_choices = [
    app_commands.Choice(name=name, value=value) for name, value in Status.items()
]


async def get_filtered_queries(category=None, difficulty=None, status=None):
    query_filter = {}
    if category:
        query_filter["category"] = category
    if difficulty:
        query_filter["difficulty"] = difficulty
    if status:
        query_filter["closed"] = status

    queries_cursor = queries_col.find(query_filter)
    queries = []
    async for query in queries_cursor:
        queries.append(query)
    return queries


async def auto_close_queries():
    seven_days_ago = datetime.datetime.utcnow() - datetime.timedelta(days=7)
    await queries_col.update_many(
        {"closed": False, "timestamp": {"$lt": seven_days_ago}},
        {"$set": {"closed": True}},
    )


class Assist(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    group = app_commands.Group(name="query", description="Query Ask")

    async def query_autocompletion(
        self, interaction: discord.Interaction, current: str
    ) -> typing.List[app_commands.Choice[str]]:
        data = []
        queries_cursor = queries_col.find(
            {}
        )  # Use the find method to query the collection
        async for (
            query
        ) in queries_cursor:  # Iterate over the cursor to construct the choices
            title_words = query["title"].split()
            for word in title_words:
                if current.lower() in map(str.lower, title_words):
                    data.append(
                        app_commands.Choice(name=query["title"], value=query["id"])
                    )
                    break
        return data

    @group.command(
        name="post",
        description="Post your query here and get answers from users from all servers. ",
    )
    @app_commands.choices(category=subject_choices)
    @app_commands.choices(difficulty=education_level_choices)
    async def post(
        self,
        ctx,
        category: app_commands.Choice[str],
        difficulty: app_commands.Choice[str],
        title: str,
        description: str,
    ):
        await ctx.response.defer(ephemeral=False)
        id = str(await queries_col.count_documents({}) + 1)
        query = {
            "id": id,
            "user_id": ctx.user.id,
            "category": category.value,
            "difficulty": difficulty.value,
            "title": title,
            "description": description,
            "timestamp": ctx.created_at.timestamp(),
            "guild_id": ctx.guild.id,
            "votes": 0,
            "voted_users": [],
            "messages": [],
            "closed": False,
        }
        # Insert the query into the queries collection
        await queries_col.insert_one(query)
        embed = discord.Embed(title=f"**{title}**", color=theme)
        author_string = f"{str(ctx.user.name)} [{str(ctx.user.id)}] ∙ {difficulty.name}"
        embed.set_author(name=author_string, icon_url=ctx.user.avatar.url)
        embed.add_field(name="Upvote", value="0")
        embed.add_field(name="Category", value=f"`{category.name}`")
        embed.add_field(name="Reward", value="20 XP")
        timestamp = format_dt(ctx.created_at, "R")
        des = f"**{id}** ∙ Posted in {ctx.guild.name} , {timestamp}\n{divider}\n **{description}**"
        embed.description = des
        xp_message = await funcs.add_xp(ctx.user.id, 50)
        if xp_message:
            await ctx.followup.send(embed=xp_message)
        sent_embed = dembed(
            title="Query posted",
            description="Keep your direct messages open to receive answers.\nYou earned 50 xp to post a query",
            color=funcs.secondary_theme,
        )
        sent_embed.add_field(name="Query", value=title, inline=False)
        original_message = await ctx.followup.send(embed=sent_embed)
        data = await incoming.find().to_list(length=None)
        for x in data:
            try:
                guild = await self.bot.fetch_guild(int(x["id"]))
                channel = self.bot.get_channel(int(x["channel"]))

                view = assetsb.Qrscontrol()
                view.add_item(
                    discord.ui.Button(
                        label="Community",
                        style=discord.ButtonStyle.link,
                        url="https://discord.gg/Nvts32BAwr",
                    )
                )
                # view.add_item(assetsb.dynamic_add_answer(ctx.user.id))
                # view.add_item(assetsb.dynamic_upvote(ctx.user.id))
                # view.add_item(assetsb.dynamic_report(ctx.user.id))
                msg = await channel.send(
                    content="### New Query", embed=embed, view=view
                )

                fq = await queries_col.find_one({"id": id})
                fq["messages"].append(
                    {"channel": str(channel.id), "msg": msg.id, "guild": str(guild.id)}
                )
                await queries_col.replace_one({"id": id}, fq)
                view.message = msg
                self.bot.add_view(view)
            except Exception as e:
                print(e)
        successfully_posted = discord.ui.View(timeout=None)
        successfully_posted.add_item(
            discord.ui.Button(
                label="Successfully Posted",
                style=discord.ButtonStyle.primary,
                disabled=True,
            )
        )
        await original_message.edit(embed=sent_embed, view=successfully_posted)

    @group.command(name="answer", description="Answer someone's query")
    @app_commands.autocomplete(query_id=query_autocompletion)
    async def answer_query(self, ctx, query_id: str, answer: str):
        await ctx.response.defer(ephemeral=False)
        query = await queries_col.find_one({"id": query_id})
        title = query.get("title")
        if not query:
            await ctx.followup.send(
                embed=dembed(
                    description="Query with ID {query_id} not found.",
                    color=discord.Color.red(),
                )
            )
            return
        user_id = ctx.user.id
        if query["closed"] == True:
            await ctx.followup.send(
                embed=dembed(description="That query is no longer accepting answers.")
            )
            return
        for answer in query.get("answers", []):
            if answer.get("user") == user_id:
                await ctx.followup.send(
                    embed=dembed(description="You have already answered this query.")
                )
                return
        if user_id == query.get("user_id"):
            await ctx.followup.send(
                embed=dembed(description="You cannot answer your own query.")
            )
            return
        # Add the answer to the query document
        if "answers" not in query:
            query["answers"] = []

        user_id = ctx.user.id
        query["answers"].append({"ans": answer, "user": user_id})

        # Update the query in the database
        result = await queries_col.replace_one({"id": query_id}, query)

        if result.modified_count == 0:
            await ctx.followup.send(
                embed=dembed(description="Failed to update query.\nPlease retry ")
            )
            return
        title = query.get("title")
        # Get the asker user ID
        des = f"### {title}\nAnswered on {ctx.guild.name}\n{divider}\n{query_id}\n{title}\n{divider}\n**### Answer**\n {answer}"
        original_questioner_id = query.get("user_id")
        embed = dembed(title="New Answer", description=des, color=theme)
        embed.set_author(name=ctx.user.name, icon_url=ctx.user.avatar.url)
        embed.set_footer(text=f"{str(ctx.user.name)} [{str(ctx.user.id)}]")
        xp_message = await funcs.add_xp(ctx.user.id, 20)
        if xp_message:
            await ctx.followup.send(embed=xp_message)
        await ctx.followup.send(
            embed=dembed(description="Query answered successfully\nYou earned 20 XP")
        )
        # Send a DM to the asker with the new answer
        if original_questioner_id:
            try:
                view = assetsb.answer_control_view()
                await original_questioner_id.send(
                    "New Answer Received 📩", embed=embed, view=view
                )
            except Exception as e:
                print(f"Cant send message to original questioner {e}")

    @group.command(name="list", description="List all the queries")
    @app_commands.choices(category=subject_choices)
    @app_commands.choices(difficulty=education_level_choices)
    @app_commands.choices(status=status_choices)
    async def list_queries(
        self,
        ctx,
        *,
        category: app_commands.Choice[str] = None,
        difficulty: app_commands.Choice[str] = None,
        status: app_commands.Choice[str] = True,
    ):
        if status.value == "False":
            status.value = False
        else:
            status.value = True
        if not category and not difficulty:
            await ctx.response.defer()
            queries = await get_filtered_queries(status=status.value)
            menu_title = f"All Queries on {self.bot.name}"
            if category:
                menu_title = f"Queries in {category.value}"
            elif difficulty:
                menu_title = f"Queries in {difficulty.value}"
            menu = ViewMenu(
                ctx,
                menu_type=ViewMenu.TypeEmbedDynamic,
                rows_requested=1,
                custom_embed=dembed(title=menu_title),
            )
            for x in queries:
                id = x["id"]
                title = x["title"]
                desc = x["description"]
                time = round(x["timestamp"])
                category = x["category"]
                difficulty = x["difficulty"]
                guild = await self.bot.fetch_guild(x["guild_id"])
                closed = x["closed"]
                status = "Yes" if not closed else " No"
                # Get the total number of answers
                num_answers = len(x.get("answers", []))

                # Replace category in the description with an empty string if category is provided
                category_text = f"**Category:** {category}" if not category else ""
                # Replace difficulty in the description with an empty string if difficulty is provided
                difficulty_text = (
                    f"**Difficulty:** {difficulty}" if not difficulty else ""
                )

                # Format the description string with all the available information
                des = f"**ID:** {id}\n**Title:** {title}\n**Description:** {desc}\n{category_text}\n{difficulty_text}\n**Created:** <t:{time}:R>\n**Guild:** {guild.name}\n**Open:** {status}\n**Total Answers:** {num_answers}"
                menu.add_row(des)

            # ViewButton.ID_PREVIOUS_PAGE
            back_button = ViewButton(
                style=discord.ButtonStyle.primary,
                label="Back",
                custom_id=ViewButton.ID_PREVIOUS_PAGE,
            )
            menu.add_button(back_button)

            # ViewButton.ID_NEXT_PAGE
            next_button = ViewButton(
                style=discord.ButtonStyle.secondary,
                label="Next",
                custom_id=ViewButton.ID_NEXT_PAGE,
            )
            menu.add_button(next_button)
            await menu.start()
        elif difficulty and not category:
            queries = await get_filtered_queries(
                difficulty=difficulty.value, status=status.value
            )
            menu_title = f"Queries in {difficulty.value}"
            menu = ViewMenu(
                ctx,
                menu_type=ViewMenu.TypeEmbedDynamic,
                rows_requested=1,
                custom_embed=dembed(title=menu_title),
            )
            for x in queries:
                id = x["id"]
                title = x["title"]
                desc = x["description"]
                time = round(x["timestamp"])
                category = x["category"]
                difficulty = x["difficulty"]
                guild = await self.bot.fetch_guild(x["guild_id"])
                closed = x["closed"]
                status = "Yes" if not closed else " No"
                # Get the total number of answers
                num_answers = len(x.get("answers", []))

                # Replace category in the description with an empty string if category is provided
                category_text = f"**Category:** {category}" if not category else ""

                # Format the description string with all the available information
                des = f"**ID:** {id}\n**Title:** {title}\n**Description:** {desc}\n{category_text}\n**Created:** <t:{time}:R>\n**Guild:** {guild.name}\n**Open:** {status}\n**Total Answers:** {num_answers}"
                menu.add_row(des)

            # ViewButton.ID_PREVIOUS_PAGE
            back_button = ViewButton(
                style=discord.ButtonStyle.primary,
                label="Back",
                custom_id=ViewButton.ID_PREVIOUS_PAGE,
            )
            menu.add_button(back_button)

            # ViewButton.ID_NEXT_PAGE
            next_button = ViewButton(
                style=discord.ButtonStyle.secondary,
                label="Next",
                custom_id=ViewButton.ID_NEXT_PAGE,
            )
            menu.add_button(next_button)
            await menu.start()
        elif category and not difficulty:
            queries = await get_filtered_queries(
                category=category.value, status=status.value
            )
            menu_title = f"Queries in {category.value}"
            menu = ViewMenu(
                ctx,
                menu_type=ViewMenu.TypeEmbedDynamic,
                rows_requested=1,
                custom_embed=dembed(title=menu_title),
            )
            for x in queries:
                id = x["id"]
                title = x["title"]
                desc = x["description"]
                time = round(x["timestamp"])
                category = x["category"]
                difficulty = x["difficulty"]
                guild = await self.bot.fetch_guild(x["guild_id"])
                closed = x["closed"]
                status = "Yes" if not closed else " No"
                # Get the total number of answers
                num_answers = len(x.get("answers", []))

                # Replace difficulty in the description with an empty string if difficulty is provided
                difficulty_text = (
                    f"**Difficulty:** {difficulty}" if not difficulty else ""
                )

                # Format the description string with all the available information
                des = f"**ID:** {id}\n**Title:** {title}\n**Description:** {desc}\n**Category:** {category}\n{difficulty_text}\n**Created:** <t:{time}:R>\n**Guild:** {guild.name}\n**Open:** {status}\n**Total Answers:** {num_answers}"
                menu.add_row(des)

            # ViewButton.ID_PREVIOUS_PAGE
            back_button = ViewButton(
                style=discord.ButtonStyle.primary,
                label="Back",
                custom_id=ViewButton.ID_PREVIOUS_PAGE,
            )
            menu.add_button(back_button)

            # ViewButton.ID_NEXT_PAGE
            next_button = ViewButton(
                style=discord.ButtonStyle.secondary,
                label="Next",
                custom_id=ViewButton.ID_NEXT_PAGE,
            )
            menu.add_button(next_button)
            await menu.start()
        elif category and difficulty:
            queries = await get_filtered_queries(
                category=category.value,
                difficulty=difficulty.value,
                status=status.value,
            )
            menu_title = f"Queries in {category.value} - {difficulty.name}"
            menu = ViewMenu(
                ctx,
                menu_type=ViewMenu.TypeEmbedDynamic,
                rows_requested=1,
                custom_embed=dembed(title=menu_title),
            )
            for x in queries:
                id = x["id"]
                title = x["title"]
                desc = x["description"]
                time = round(x["timestamp"])
                category = x["category"]
                difficulty = x["difficulty"]
                guild = await self.bot.fetch_guild(x["guild_id"])
                closed = x["closed"]
                status = "Yes" if not closed else " No"
                # Get the total number of answers
                num_answers = len(x.get("answers", []))

                # Format the description string with all the available information
                des = f"**ID:** {id}\n**Title:** {title}\n**Description:** {desc}\n**Category:** {category}\n**Difficulty:** {difficulty}\n**Created:** <t:{time}:R>\n**Guild:** {guild.name}\n**Open:** {status}\n**Total Answers:** {num_answers}"
                menu.add_row(des)

            # ViewButton.ID_PREVIOUS_PAGE
            back_button = ViewButton(
                style=discord.ButtonStyle.primary,
                label="Back",
                custom_id=ViewButton.ID_PREVIOUS_PAGE,
            )
            menu.add_button(back_button)

            # ViewButton.ID_NEXT_PAGE
            next_button = ViewButton(
                style=discord.ButtonStyle.secondary,
                label="Next",
                custom_id=ViewButton.ID_NEXT_PAGE,
            )
            menu.add_button(next_button)
            await menu.start()

    @group.command(
        name="channel", description="Set channel where you receive all the queries"
    )
    @commands.has_permissions(manage_messages=True)
    async def set_incoming_channel(
        self, ctx, *, channel: discord.TextChannel = None, disable: bool = False
    ):
        await ctx.response.defer()
        if not disable:
            results = await incoming.find_one({"id": ctx.guild.id})
            if not results:
                query = {"id": ctx.guild.id, "channel": channel.id}
                await incoming.insert_one(query)

            else:
                await incoming.update_one(
                    {"id": ctx.guild.id}, {"$set": {"channel": channel.id}}
                )
            await ctx.followup.send(
                embed=dembed(
                    description=f"Successfully Set Incoming  Channel for receiving queries \t {channel.mention}"
                )
            )
        elif disable:
            results = await incoming.find_one({"id": ctx.guild.id})
            if not results:
                return await ctx.followup.send(
                    "You haven't set any incoming channel yet"
                )
            channel = await self.bot.get_channel(incoming.get("channel"))
            await incoming.delete_one({"id": ctx.guild.id})
            await ctx.followup.send(
                embed=dembed(
                    description=f"Successfully unset {channel.mention} as incoming channel for receiving queries"
                )
            )

    @group.command(
        name="close",
        description="Close a query...Closed queries no longer accept answers",
    )
    @commands.guild_only()
    async def close_query(self, ctx, query_id: str):
        await ctx.response.defer()
        incoming_channel = await incoming.find_one({"id": ctx.guild.id})
        if (
            not incoming_channel
            or not incoming_channel.get("channel") == ctx.channel.id
        ):
            await ctx.followup.send(
                embed=dembed(
                    description="Invalid Channel\n Please use the chosen query channel or set one..."
                )
            )
            return
        # Find the query in the database
        query = await queries_col.find_one({"id": query_id})

        if not query:
            await ctx.followup.send(
                embed=dembed(description=f"Query with ID {query_id} not found.")
            )
            return

        # Check if the user has permission to close the query
        if ctx.user.id != query.get("user_id"):
            await ctx.followup.send(
                embed=dembed(
                    description="You do not have permission to close this query."
                )
            )
            return

        # Check if the query is already closed
        if query.get("closed"):
            await ctx.followup.send(
                embed=dembed(description="This query is already closed.")
            )
            return

        # Close the query
        query["closed"] = True
        await queries_col.replace_one({"id": query_id}, query)

        # Inform the user that the query has been closed
        await ctx.followup.send(
            embed=dembed(
                description=f"Query with ID {query_id} has been closed and will no longer accept answers"
            )
        )

    # Start the auto-close task loop
    @tasks.loop(hours=72)
    async def auto_close_loop(self):
        await auto_close_queries()


async def setup(bot):
    await bot.add_cog(Assist(bot))
