from __future__ import annotations
import discord
import utils.functions as funcs
import datetime
import motor.motor_asyncio
import nest_asyncio
import os
import discord.utils
import datetime
import re
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
        emoji="🔒",
    )
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        query_id = self.message.embeds[0].description.split("\n")[3]
        print(self)
        query = await queries_col.find_one({"_id": query_id})
        query["closed"] = True
        await queries_col.replace_one({"_id": query_id}, query)
        await interaction.response.send_message("Query Closed", ephemeral=True)










class dynamic_add_answer(discord.ui.DynamicItem[discord.ui.Button], template=r'persistent_view:answer:user:(?P<id>[0-9]+)'):
  def __init__(self, user_id: int) -> None:
      super().__init__(
          discord.ui.Button(
              label="Answer",
              style=discord.ButtonStyle.success,
              emoji="📄",
              custom_id=f'persistent_view:answer:user:{user_id}',
          )
      )
      

  # This is called when the button is clicked and the custom_id matches the template.
  @classmethod
  async def from_custom_id(cls, interaction: discord.Interaction, item: discord.ui.Button, match: re.Match[str], /):
      user_id = int(match['id'])
      return cls(user_id)



  async def callback(self, interaction: discord.Interaction) -> None:
      msg_id=interaction.message.id
      query = await queries_col.find_one({"messages": {"$elemMatch": {"msg": msg_id}}})
      query_id=query["_id"]
      await interaction.response.send_message(
          f"Use command\n**</query answer:1085572802976952340> id {query_id}**\nModal boxes for answers coming soon...",
          ephemeral=True,
      )
class dynamic_upvote(discord.ui.DynamicItem[discord.ui.Button], template=r'persistent_view:vote:user:(?P<id>[0-9]+)'):
  def __init__(self, user_id: int) -> None:
      super().__init__(
          discord.ui.Button(
              label="Upvote",
              style=discord.ButtonStyle.blurple,
              emoji="🔼",
              custom_id=f'persistent_view:vote:user:{user_id}',
          )
      )
      

  # This is called when the button is clicked and the custom_id matches the template.
  @classmethod
  async def from_custom_id(cls, interaction: discord.Interaction, item: discord.ui.Button, match: re.Match[str], /):
      user_id = int(match['id'])
      return cls(user_id)



  async def callback(self, interaction: discord.Interaction) -> None:
      msg_id=interaction.message.id
      query = await queries_col.find_one({"messages": {"$elemMatch": {"msg": msg_id}}})
      query_id=query["_id"]
      voted_users = query.get("voted_users", [])
  
      if interaction.user.id in voted_users:
          query["votes"] -= 1
          voted_users.remove(interaction.user.id)
          await interaction.response.send_message(
              embed=funcs.dembed(description="Removed your vote"), ephemeral=True
          )
      else:
          query["votes"] += 1
          voted_users.append(interaction.user.id)
          await interaction.response.send_message(
              embed=funcs.dembed(description="Added your vote"), ephemeral=True
          )
  
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
class dynamic_report(discord.ui.DynamicItem[discord.ui.Button], template=r'persistent_view:report:user:(?P<id>[0-9]+)'):
  def __init__(self, user_id: int) -> None:
      super().__init__(
          discord.ui.Button(
              label="Report",
              style=discord.ButtonStyle.red,
              emoji="🚨",
              custom_id=f'persistent_view:report:user:{user_id}',
          )
      )
      

  
  @classmethod
  async def from_custom_id(cls, interaction: discord.Interaction, item: discord.ui.Button, match: re.Match[str], /):
      user_id = int(match['id'])
      return cls(user_id)



  async def callback(self, interaction: discord.Interaction) -> None:
      msg_id=interaction.message.id
      query = await queries_col.find_one({"messages": {"$elemMatch": {"msg": msg_id}}})
      query_id=query["_id"]
      title=query["title"]
      description=query["description"]
      difficulty=query["difficulty"]
      user=query["user_id"]
      upvotes=query["votes"]
      category=query["category"]
      embed = discord.Embed(title=f"**{title}**",description=description, color=funcs.theme)
      authr = f"{user} ∙ {difficulty}"
      embed.set_author(name=interaction.user, icon_url=interaction.user.avatar.url)
      embed.add_field(name="Upvotes", value=upvotes)
      embed.add_field(name="Category", value=f"`{category}`")
      await interaction.client.get_channel(979345665081610271).send(f" {interaction.user.mention} Reported the following query",embed=embed)
      await interaction.response.send_message("Sent the report to the bot moderators")
