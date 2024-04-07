import os
import discord
import psutil
from discord import app_commands
from discord.ext import commands
import motor.motor_asyncio
import nest_asyncio
import json
import random
import utils.functions as funcs
import utils.economy as economy_functions
from utils.functions import dembed, theme, divider
from dotenv import load_dotenv

nest_asyncio.apply()


os.chdir("..")
load_dotenv()
nest_asyncio.apply()

mongo_url = os.environ["mongodb"]

cluster = motor.motor_asyncio.AsyncIOMotorClient(mongo_url)
economy_collection = cluster["accumen"]["economy"]

coin_emoji = ''
gem_emoji = ''
class Economy_Basic(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    @app_commands.command(name="balance", description="Shows your balance")
    async def balance(self, ctx, user: discord.Member = None):
        if user is None:
            user = ctx.user
        try:
            bal = await economy_functions.get_user_data(user.id)
            if bal is None:
                await self.open_account(user.id)
                await economy_functions.get_user_data(user.id)
            embed = dembed(
                title=f"{user.name}'s Balance",
                description=f"{user.mention}'s balance is a wondrous sight to behold.\n",
                thumbnail=user.avatar.url
            )

            embed.add_field(name="Coins", value=f"{coin_emoji} {bal["coins"]}", inline=True)

            embed.add_field(name="Gems", value=f"{gem_emoji} {bal["gems"]}", inline=True)
            
            embed.set_footer(icon_url=ctx.user.avatar.url)
            await ctx.response.send_message(embed=embed)
        except Exception as e:
            await ctx.send(f"An error occurred {e}")


async def setup(bot):
    await bot.add_cog(Economy_Basic(bot))
