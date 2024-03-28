import hashlib
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
import random
class Academia(commands.Cog):     
    def __init__(self, bot: commands.Bot) -> None:   # Initialize the class with the bot object
        """
        Initialize the Academia class with the bot object.

        :param bot: The bot object that this cog is associated with.
        :type bot: commands.Bot
        :return None
        """
        self.bot = bot
        self.data = {}
        #self.delete_data.start()
        self.anonymous_chat_channel_id=1197779801432391780
        self.academia_server_id=1197779801432391780
        self.moderator_role_id=1049696198556131380


    group = app_commands.Group(
        name="academia",
        description="Academia only commands",
        guild_ids=[self.academia_server_id],
      
    )
    @commands.command(name="pseudo", description="Send message pseudonymously")
    async def send_pseudonymous_message(self, ctx, message: str):
        if ctx.user.id in self.data:
            id_ = self.data[ctx.user.id]
        else:
            id_ = hashlib.sha256(f"{ctx.user.id}{random.random()}".encode()).hexdigest()
            self.data[ctx.user.id] = id_

        channel = self.bot.get_channel(self.anonymous_chat_channel_id)
        embed = dembed(description=message)
        embed.set_footer(text=f"Sent by {id_}")
        await channel.send(embed=embed)
        await ctx.response.send_message("Message sent", ephemeral=True)

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
        # [TODO] store all ids, server ids , channel ids etc. in init func while setting up the cog
        server = message.guild
        if not server or server.id != self.academia_server_id:
            return

        if len(message.content) < 5 or message.author.bot:
            return  # Skip short messages and messages from bots
        
        # Get the "Moderator" role and the number of online members with that role
        moderator_role = discord.utils.get(server.roles, id=self.moderator_role_id)
        if not moderator_role:
            return
        # count users in online if there status is either online or do not disturb
        online_moderators = sum(1 for member in server.members if moderator_role in member.roles and member.status == discord.Status.online)

        # Check if more than 50% of the online members with the  role are currently online
        if online_moderators > server.member_count / 2:
            return

        channel = self.bot.get_channel(message.channel.id)
        moderation = automod.text_moderation(message.content)
        if moderation[0]:  # Check if the first value of the tuple is True
            await message.delete()

            # Create an embed with detailed information about the moderation action
            embed = dembed(title="Message Blocked", description="This message has been automatically blocked due to the following reasons:", color=discord.Color.red())

            # Add fields to the embed to provide more information
            embed.add_field(name="Reason", value=moderation[1], inline=False)
            embed.add_field(name="Author", value=message.author.mention, inline=True)
            embed.add_field(name="Channel", value=channel.mention, inline=True)
            embed.set_footer(text="This message has been automatically moderated.")

            await channel.send(embed=embed)

        
async def setup(bot):
    await bot.add_cog(Academia(bot))
