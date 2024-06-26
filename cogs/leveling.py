import discord
from discord.ext import commands
from discord import app_commands
import os
import utils.economy as economy
from utils.functions import dembed
from reactionmenu import ViewMenu, ViewButton
import motor.motor_asyncio
import nest_asyncio
import random

# from DiscordLevelingCard import RankCard, Settings
nest_asyncio.apply()
mongo_url = os.environ["mongodb"]
cluster = motor.motor_asyncio.AsyncIOMotorClient(mongo_url)
levelling = cluster["accumen"]["level"]


class Levels(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    group = app_commands.Group(name="level", description="Execute leveling commands")

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
                if xp < ((50 * (lvl**2)) + (50 * (lvl))):
                    break
                lvl += 1
            xp -= (50 * ((lvl - 1) ** 2)) + (50 * (lvl - 1))

            if xp == 0:
                user_data = await economy.get_user_data(user_id)
                await economy.add_coins(user_id, lvl * 10)
                await economy.add_gems(user_id, lvl)
                embed = dembed(
                    description=f"Congratulations <@{user_id}>! You leveled up to **level {lvl}**",
                )
                embed.add_field(name="Coins earned", value=lvl * 10)
                embed.add_field(name="Gems earned", value=lvl)
                return embed

    @commands.Cog.listener()
    async def on_interaction(self, interaction):
        if str(interaction.type) == "InteractionType.application_command":

            xp_message = await self.add_xp(interaction.user.id, random.randint(5, 15))
            if xp_message:
                await interaction.channel.send(embed=xp_message)

    @group.command(name="rank", description="Shows your xp and global rank")
    async def rank(self, ctx, user: discord.Member = None):
        user = user or ctx.user
        await ctx.response.defer()
        stats = await levelling.find_one({"id": ctx.user.id})
        if stats is None:
            await ctx.followup.send("You haven't sent any messages, no rank!")

        else:
            xp = stats["xp"]
            lvl = 0
            rank = 0

            while True:
                if xp < ((50 * (lvl**2)) + (50 * (lvl))):
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
            max_xp = int(200 * ((1 / 2) * lvl))
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
            # image = await card.card3()
            message = (
                f"Name: **{ctx.user.mention}**\n"
                f"XP: **{xp}/{int(200 * ((1 / 2) * lvl))}**\n"
                f"Global Rank: **{rank}**\n"
                f"Level: **{lvl}**\n"
                f"Progress Bar :\n**{progress_bar}**\n"
            )
            embed = dembed(description=message, thumbnail=ctx.user.avatar.url)
            await ctx.followup.send(
                embed=embed,
                # file=discord.File(image, filename="rank.png")
            )

    @group.command(name="leaderboard", description="Shows the global leaderboard")
    async def lb(self, ctx):
        await ctx.response.send_message(
            embed=dembed(description="Wait till I fetch the latest details")
        )
        rankings = levelling.find().sort("xp", -1)
        i = 1
        embed = dembed(
            title="Global Leaderboard",
        )
        menu = ViewMenu(
            ctx,
            menu_type=ViewMenu.TypeEmbedDynamic,
            rows_requested=5,
            delete_interactions=True,
            delete_items_on_timeout=True,
            timeout=10,
        )
        async for x in rankings:
            try:
                user = ctx.guild.get_member(x["id"])
                user_xp = x["xp"]
                text = f"{i} : {user.display_name}\nXP: {user_xp}"
                i += 1
                menu.add_row(text)
            except:
                pass
            if i == 11:
                break

        embed.set_footer(
            text=f"Requested By: {ctx.user.name}",
            icon_url=f"{ctx.user.avatar.url}",
        )
        back_button = ViewButton(
            style=discord.ButtonStyle.secondary,
            label="Back",
            emoji="◀",
            custom_id=ViewButton.ID_PREVIOUS_PAGE,
        )
        menu.add_button(back_button)

        next_button = ViewButton(
            style=discord.ButtonStyle.primary,
            label="Next",
            emoji="▶",
            custom_id=ViewButton.ID_NEXT_PAGE,
        )
        menu.add_button(next_button)

        stop_button = ViewButton(
            style=discord.ButtonStyle.danger,
            label="Stop",
            emoji="🛑",
            custom_id=ViewButton.ID_END_SESSION,
        )
        menu.add_button(stop_button)
        menu.set_main_pages(embed)
        await menu.start()


async def setup(bot):
    await bot.add_cog(Levels(bot))
