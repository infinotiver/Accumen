import discord
import json
from discord.ext import commands,tasks
from discord import app_commands
import requests
import os
import utils.functions as funcs
from utils.functions import dembed
import utils.academia as acutils
import utils.automod as automod
class Academia(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.data={}
        #self.delete_data.start()
    group = app_commands.Group(
        name="academia",
        description="Academia only commands",
        guild_ids=[976878887004962917],
      
    )
    @group.command(name="pseudo", description="Send message pseudonymously")
    async def pseudonymous(self,ctx,message:str):
      if ctx.user.id in self.data:
        id=self.data[ctx.user.id]
      else:
        id=acutils.gen_random_id(length=7)
        self.data[ctx.user.id]=id
      channel=self.bot.get_channel(1197779801432391780)
      embed=dembed(description=message)
      embed.set_author(name=id)
      await channel.send(embed=embed)
      await ctx.response.send_message("Message sent",ephemeral=True)

    @tasks.loop(seconds = 300) 
    async def delete_data(self):
     #self.data={}
     pass
    @group.command(name="reload",description="Reload cogs")
    @commands.is_owner()
    async def reload(self,ctx):
      await ctx.response.defer()
      # Define the base directory where your project resides
      base_dir = os.path.dirname(os.path.abspath(__file__))

      # Construct the path to the "cogs" directory relative to the base directory
      cogs_dir = os.path.join(base_dir) 

      for filename in os.listdir(cogs_dir):
          if filename.endswith(".py"):
              try:
                  await self.bot.unload_extension(f"cogs.{filename[:-3]}")
                  await self.bot.load_extension(f"cogs.{filename[:-3]}")
      
              except Exception as e:
                 print(e)
      await ctx.followup.send("Cogs Reloaded")
    @commands.Cog.listener()
    async def on_message(self, message):
        server = message.guild
        if not server or server.id != 976878887004962917:
            return

        if len(message.content) < 5 or message.author.bot:
            return  # Skip short messages and messages from bots

        channel = self.bot.get_channel(message.channel.id)
        moderation = automod.text_moderation(message.content)
        if moderation[0]:  # Check if the first value of the tuple is True
            await message.delete()

            # Create an embed with detailed information about the moderation action
            embed = discord.Embed(title="Message Blocked", description="This message has been automatically blocked due to the following reasons:", color=discord.Color.red())

            # Add fields to the embed to provide more information
            embed.add_field(name="Reason", value=moderation[1], inline=False)
            embed.add_field(name="Author", value=message.author.mention, inline=True)
            embed.add_field(name="Channel", value=channel.mention, inline=True)
            embed.set_footer(text="This message has been automatically moderated.")

            await channel.send(embed=embed)

        
async def setup(bot):
    await bot.add_cog(Academia(bot))
