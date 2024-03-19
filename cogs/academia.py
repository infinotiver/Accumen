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
            embed = dembed(title="Message Blocked", description=moderation[1])
            await channel.send(embed=embed)

        
async def setup(bot):
    await bot.add_cog(Academia(bot))
