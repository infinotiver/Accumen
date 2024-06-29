import os
import discord
from discord import app_commands
from discord.ext import commands
import motor.motor_asyncio
import nest_asyncio
import utils.economy as economy_functions
from utils.functions import dembed
from dotenv import load_dotenv

nest_asyncio.apply()


os.chdir("..")
load_dotenv()
nest_asyncio.apply()

mongo_url = os.environ["mongodb"]

cluster = motor.motor_asyncio.AsyncIOMotorClient(mongo_url)
economy_collection = cluster["accumen"]["economy"]

coin_emoji = "<:c_:1090623584432570440>"
gem_emoji = "<:d_:1090623594893160458>"


class Economy_Basic(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="balance", description="Shows your balance")
    async def balance(self, ctx, user: discord.Member = None):
        user = user or ctx.user
        try:
            bal = await economy_functions.get_user_data(user.id)
            embed = dembed(
                title=f"{user.display_name}'s Balance", thumbnail=user.avatar.url
            )
            embed.add_field(
                name="Coins", value=f"{coin_emoji} {bal['coins']}", inline=True
            )
            embed.add_field(
                name="Gems", value=f"{gem_emoji} {bal['gems']}", inline=True
            )
            embed.set_footer(icon_url=ctx.user.avatar)

            await ctx.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            await ctx.response.send_message(f"An error occurred: {e}", ephemeral=True)


async def setup(bot):
    await bot.add_cog(Economy_Basic(bot))
