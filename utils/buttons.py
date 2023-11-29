import discord
import utils.functions as funcs
import datetime
import motor.motor_asyncio
import nest_asyncio
import os
import discord.utils

nest_asyncio.apply()

mongo_url = os.environ["mongodb"]

cluster = motor.motor_asyncio.AsyncIOMotorClient(mongo_url)
queries_col = cluster["accumen"]["queries"]
incoming = cluster["accumen"]["incoming"]
class answercontrol(discord.ui.View):
  
  def __init__(self):
    super().__init__(timeout=None)

  @discord.ui.button(
    label="Close Query",
    style=discord.ButtonStyle.danger,
    custom_id="persistent_view:close_query",
    emoji="🔒"
  )
  async def close(self,interaction:discord.Interaction,button:discord.ui.Button):
    query_id=self.message.embeds[0].description.split("\n")[3]
    query = await queries_col.find_one({"_id": query_id})
    query["closed"] = True
    await queries_col.replace_one({"_id": query_id}, query)
    await interaction.response.send_message(
      "Query Closed",ephemeral=True
    )
# for assist.py --- User control panel (cmd = new)
class Qrscontrol(discord.ui.View):

  def __init__(self):
    super().__init__(timeout=None)


  @discord.ui.button(
    label="Add an Answer",
    style=discord.ButtonStyle.success,
    custom_id="persistent_view:answer",
    emoji="✒"
  )
  async def ans(self, interaction: discord.Interaction,
                button: discord.ui.Button):

    query_id = self.message.embeds[0].description.split("\n")[0].split("**")[1]

    await interaction.response.send_message(
      f"Use command\n**</query answer:1085572802976952340> id {query_id}**", ephemeral=True)


  @discord.ui.button(
    label="Upvote",
    style=discord.ButtonStyle.blurple,
    custom_id="persistent_view:vote",
    emoji="🔼"
  )
  async def vote(self, interaction: discord.Interaction,
                 button: discord.ui.Button):
    query_id = self.message.embeds[0].description.split("\n")[0].split("**")[1]
    query = await queries_col.find_one({"_id": query_id})
    voted_users = query.get("voted_users", [])

    if interaction.user.id in voted_users:
      query["votes"] -= 1
      voted_users.remove(interaction.user.id)
      await interaction.response.send_message(embed=funcs.dembed(description="Removed vote"), ephemeral=True)
    else:
      query["votes"] += 1
      voted_users.append(interaction.user.id)
      await interaction.response.send_message(embed=funcs.dembed(description="Added vote"), ephemeral=True)

    await queries_col.replace_one({"_id": query_id}, query)

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
    emoji="🛑"
  )
  async def report(self, interaction: discord.Interaction,
                   button: discord.ui.Button):
    pass