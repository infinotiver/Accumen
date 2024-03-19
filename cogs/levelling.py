import discord
from discord.ext import commands
from discord import app_commands
import requests
import os
import utils.functions as funcs
from utils.functions import dembed, theme, divider
import urllib.parse
from reactionmenu import ViewMenu, ViewButton
import motor.motor_asyncio
import nest_asyncio
import random
#from DiscordLevelingCard import RankCard, Settings
nest_asyncio.apply()
mongo_url = os.environ["mongodb"]
cluster = motor.motor_asyncio.AsyncIOMotorClient(mongo_url)
levelling = cluster["accumen"]["level"]

class Levels(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    group = app_commands.Group(
        name="levels", description="Execute level-related commands."
    )
    async def add_xp(self, user_id, xp_amount):
      stats = await levelling.find_one({"id": user_id})
    
      if stats is None:
          new_user = {"id": user_id, "xp": xp_amount}
          await levelling.insert_one(new_user)
      else:
          xp = stats["xp"] + xp_amount
          levelling.update_one({"id": user_id}, {"$set": {"xp": xp}})
    
          lvl = 0
          while True:
              if xp < ((50 * (lvl ** 2)) + (50 * (lvl))):
                  break
              lvl += 1
          xp -= (50 * ((lvl - 1) ** 2)) + (50 * (lvl - 1))
    
          if xp == 0:
              return dembed(description=f"Well done <@{user_id}>! You leveled up to **level: {lvl}**")
    @commands.Cog.listener()
    async def on_interaction(self, interaction):
        if str(interaction.type) == "InteractionType.application_command":
              xp_message = await self.add_xp(interaction.user.id, random.randint(5, 15))
              if xp_message:
                  await interaction.channel.send(embed=xp_message)
    @group.command(name="rank",description="Shows your xp and global rank")
    async def rank(self, ctx,
                   #user:discord.Member
                  ):
      await ctx.response.defer()
      stats = await levelling.find_one({"id": ctx.user.id})
      if stats is None:
          await ctx.followup.send("You haven't sent any messages, no rank!")

      else:
          xp = stats["xp"]
          lvl = 0
          rank = 0

          while True:
              if xp < ((50 * (lvl ** 2)) + (50 * (lvl))):
                  break
              lvl += 1
          xp -= (50 * ((lvl - 1) ** 2)) + (50 * (lvl - 1))

          rankings = levelling.find().sort("xp", -1)

          async for x in rankings:
              rank += 1
              if stats["id"] == x["id"]:
                  break

          progress_bar = f"{int((xp / (200 * ((1 / 2) * lvl))) * 20) * '<:D4:1074952383605506089>'}{(20 - int((xp / (200 * ((1 / 2) * lvl))) * 20)) * '<:D11:1128533232846131282>'}"
          """
          card_settings = Settings(
              text_color="white",
              bar_color="#8a2be2",
              background="https://img.freepik.com/free-vector/abstract-design-background-with-blue-purple-gradient_1048-13167.jpg",
          )
          """
          max_xp=int(200 * ((1 / 2) * lvl))
          """
          card = RankCard(
              settings=card_settings,
              avatar=ctx.user.avatar.url,
              level=lvl,
              current_exp=xp,
              max_exp=max_xp,
              username=ctx.user.display_name
          )
          """
          #image = await card.card3()
          message = (
              f"{ctx.user.name}'s Level stats\n"
              f"Name: {ctx.user.mention}\n"
              f"XP: {xp}/{int(200 * ((1 / 2) * lvl))}\n"
              f"Global Rank: {rank}\n"
              f"Level: {lvl}\n"
              f"Progress Bar [lvl]: {progress_bar}\n"
          )
          embed=dembed(description=message)
          await ctx.followup.send(
            embed=embed,
            #file=discord.File(image, filename="rank.png")
          )
    @group.command(name="leaderboard",description="Shows the leaderboard")  
    async def lb(self, ctx):
      rankings = levelling.find().sort("xp", -1)
      i = 1
      embed = dembed(
          title="Rankings",
          color=theme
      )
      async for x in rankings:
          try:
              temp = ctx.guild.get_member(x["id"])
              tempxp = x["xp"]
              embed.add_field(
                  name=f"{i} : {temp.name}", value=f"XP: {tempxp}", inline=False
              )
              i += 1
          except:
              pass
          if i == 11:
              break
    
      embed.set_footer(
          text=f"Requested By: {ctx.user.name}",
          icon_url=f"{ctx.user.avatar.url}",
        
      )
    
      await ctx.channel.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Levels(bot))
