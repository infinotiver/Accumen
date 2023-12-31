import os
import asyncio
import discord
from discord.ext import commands
from discord import Button, SelectMenu, SelectOption
from discord import app_commands
import utils.system as system_utils
import utils.functions as funcs
from utils.functions import dembed, theme, divider
from discord.ext.commands import check
import json
import requests
import motor.motor_asyncio
import nest_asyncio
import typing
from reactionmenu import ViewMenu, ViewButton
import datetime

nest_asyncio.apply()
mongo_url = os.environ["mongodb"]
cluster = motor.motor_asyncio.AsyncIOMotorClient(mongo_url)
accumen_mongo = cluster["accumen"]["system"]


def devc(ctx):
    results = accumen_mongo.find_one({"_id": "developers"})
    if not results:
        data = {"_id": "developers", "developer": [900992402356043806]}
        accumen_mongo.insert_one(data)
    if ctx.user.id in results["developer"]:
        return True
    else:
        return False



class Accumen(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    group = app_commands.Group(
        name="developer", description="developer commands"
    )
    @staticmethod
    def cleanup_code(content):
        """Automatically removes code blocks from the code."""
        # remove ```py\n```
        if content.startswith("```") and content.endswith("```"):
            return "\n".join(content.split("\n")[1:-1])

        return content.strip("` \n")
    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        embed = discord.Embed(
            title="Joined a guild!",
            description=f"{guild.name} \nOwner {guild.owner}",
            color=theme,
        )
        embed.add_field(name="Server ID",value=guild.id)
        embed.add_field(
            name=f"This Guild Has {guild.member_count} Members!",
            value=f"Yay Another Server! We Are Now At {len(self.bot.guilds)} Guilds!",
        )
        await self.bot.get_channel(os.environ["dev_channel"]).send(embed=embed)
    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        embed = discord.Embed(
            title="Removed from a guild!",
            description=f"{guild.name} \nOwner {guild.owner}",
            color=theme,
        )
        embed.add_field(name="Server ID",value=guild.id)
        embed.add_field(
            name=f"This Guild Had {guild.member_count} Members!",
            value=f"We Are Now At {len(self.bot.guilds)} Guilds!",
        )
        await self.bot.get_channel(os.environ["dev_channel"]).send(embed=embed)
    @group.command(name="reboot", description="Reboot (Restart) the bot")
    @app_commands.choices(
        mode=[
            app_commands.Choice(name="Basic Restart", value=1),
            app_commands.Choice(name="Advance Reboot", value=2),
        ]
    )
    @check(devc)
    async def restart(self, ctx, mode: app_commands.Choice[int]):
        await ctx.response.send_message("Executing Command")
        for filename in os.listdir("./cogs"):
            try:
                await self.bot.unload_extension(f"cogs.{filename[:-3]}")
            except Exception as ex:
                print(f"{filename} - {ex}")
        await self.bot.change_presence(
            status=discord.Status.idle,
            activity=discord.Activity(
                type=discord.ActivityType.watching, name=f"🚀 System Reboot "
            ),
        )
        system_utils.restart_bot(mode)

    @check(devc)
    @group.command()
    async def servers(self,ctx,compact:bool=True):       
        activeservers = self.bot.guilds
        if not compact:
          for guild in activeservers:
              name=str(guild.name)
              description=str(guild.description)
              owner=str(guild.owner)
              _id = str(guild.id)
              memcount=str(guild.member_count)
              icon = str(guild.icon.url)
              ver = str(ctx.guild.verification_level)
              embed=discord.Embed(
                      title=name +" Server Information",
                      description=description,
                      color=discord.Color.blue()
                      )
              embed.set_thumbnail(url=icon)
              embed.add_field(name="Owner",value=owner,inline=True)
              embed.add_field(name="Server Id",value=_id,inline=True)
              embed.add_field(name="Member Count",value=memcount,inline=True)
              embed.add_field(name="Verification Level",value=ver,inline=True)
    
              await ctx.response.send_message(embed=embed)
        else:
          embed=discord.Embed(title="My Guilds",color=discord.Color.dark_theme())
          for guild in activeservers:
            embed.add_field(name=guild,value=f"({str(guild.id)}) -{str(guild.member_count)} **({str(guild.owner)})**",inline=False)
          await ctx.response.send_message(embed=embed) 
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if str(error) =="You are blacklisted":
          await ctx.send(embed=discord.Embed(description=f'Blacklisted user',color=discord.Color.dark_red())  ) 
          return     
        if hasattr(ctx.command, "on_error"):
            return
        #with open ("storage/errors.json", "r") as f:
            #data = json.load(f)
        error = getattr(error, "original", error)
    
        if isinstance(error, commands.BotMissingPermissions):
            missing = [
                perm.replace("_", " ").replace("guild", "server").title()
                for perm in error.missing_perms
            ]
            if len(missing) > 2:
                fmt = "{}, and {}".format("**, **".join(missing[:-1]), missing[-1])
            else:
                fmt = " and ".join(missing)
    
            embed = discord.Embed(
                title="Missing Permissions",
                description=f"I am missing **{fmt}** permissions to run this command :(",
                color=self.theme_color,
            )
    
            embed.set_author(name=ctx.user,icon_url=ctx.user.avatar_url)
            return
        elif isinstance(error, commands.CommandNotFound):
          return
        elif isinstance(error, commands.DisabledCommand):
            embed = discord.Embed(
                title="Command disabled",
                description=f"Looks like This command is disabled for use !",
                color=self.theme_color,
            )   
            await ctx.send(embed=embed)       
            return
    
        elif isinstance(error, commands.CommandOnCooldown):
    
            embed = discord.Embed(
                title="Whoa Slow it down!!!!",
                description=f"Retry that command after {datetime.timedelta(seconds=error.retry_after)}.",
                color=self.theme_color,
            )
            embed.set_author(name=ctx.user,icon_url=ctx.user.avatar_url)
            #embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/922468797108080660.png")
            await ctx.send(embed=embed)
    
            return
    
        elif isinstance(error, commands.MissingPermissions):
            missing = [
                perm.replace("_", " ").replace("guild", "server").title()
                for perm in error.missing_perms
            ]
            if len(missing) > 2:
                fmt = "{}, and {}".format("**, **".join(missing[:-1]), missing[-1])
            else:
                fmt = " and ".join(missing)
            embed = discord.Embed(
                title="Insufficient Permission(s)",
                description=f"You need the **{fmt}** permission(s) to use this command.",
                color=self.theme_color,
            )
            embed.set_author(name=ctx.user,icon_url=ctx.user.avatar_url)
            #embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/922468797108080660.png")
            await ctx.send(embed=embed)
            return
        elif isinstance(error, commands.CheckFailure):
          embed = discord.Embed(
              title="Permissions Denied",
              description=f"You do not have permissions to use this command",
              color=self.theme_color,
          )
          #embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/922468797108080660.png")
          await ctx.send(embed=embed)
          return
async def setup(bot):
    await bot.add_cog(Accumen(bot))
