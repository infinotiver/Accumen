def changelog():
    text = """

  Changelog ( With accordance to editor activity for personal use only)
  25-12-2023 - 26-12-2023
  - commited on 26-12
  """
    return text


import os
import asyncio
import discord
from discord.ext import commands
from discord import Button, SelectMenu, SelectOption
from discord import app_commands
import utils.buttons
import utils.functions as funcs
from utils.functions import dembed, theme, divider
import json
import requests
from json.decoder import JSONDecodeError


async def fetch_data(place=None):
    try:
        json_url = "https://raw.githubusercontent.com/dr5hn/countries-states-cities-database/master/countries.json"
        response = requests.get(json_url)
        response.raise_for_status()
        data = response.json()

        all_locations = []
        for country in data:
            all_locations.append(country["name"])

        if not place:
            return all_locations
        else:
            lower_place = place.lower()
            for location in all_locations:
                if lower_place == location.lower():
                    return True
            return False
    except JSONDecodeError as json_error:
        print(f"JSON decoding error: {json_error}")
        print(f"Problematic response: {response.text}")
        return None  # Handle the error appropriately in your code
    except requests.RequestException as req_error:
        print(f"Request error: {req_error}")
        return None  # Handle the error appropriately in your code


class Atlas(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.locations = []
        self.games = {}

    atlas = app_commands.Group(name="atlas", description="ATLAS GAME")

    @atlas.command(
        name="game-announce",
        description="Announce a game of ATLAS and wait for others to join ",
    )
    async def announce(self, ctx):
        await ctx.response.defer()
        embed = discord.Embed(
            title="ATLAS Announcement",
            description=(
                f"\nAllowed Places\n* Countries\n* ~~States~~\n* ~~Cities~~\n* ~~Continents~~\nStates and Cities coming soon...\n"
                f"{divider}\n Interested members use /game-enter command"
            ),
            color=theme,
        )
        msg = await ctx.followup.send(embed=embed)
        game = {
            "server": ctx.guild.id,
            "channel": ctx.channel.id,
            "users": [ctx.user.id],
            "places_done": [],
            "message": msg.id,
            "time": {"announced": ctx.created_at.timestamp(), "started": 0, "ended": 0},
        }
        self.games[str(ctx.guild.id)] = game
        print(self.games)

        embed.description += "\nSuccessfully initiated game"
        await msg.edit(embed=embed)

    @atlas.command(name="game-enter", description="Enter a game of ATLAS")
    async def enter(self, ctx):
        await ctx.response.defer()
        if str(ctx.guild.id) not in self.games:
            return await ctx.followup.send("No game is currently running")
        elif ctx.user.id in self.games[str(ctx.guild.id)]["users"]:
            return await ctx.followup.send("You are already in the game")
        elif ctx.channel.id != self.games[str(ctx.guild.id)]["channel"]:
            return await ctx.followup.send("This is not the game channel")
        elif len(self.games[str(ctx.guild.id)]["users"]) > 5:
            return await ctx.followup.send(
                "Currently , more than 5 participants can not play."
            )
        else:
            self.games[str(ctx.guild.id)]["users"].append(ctx.user.id)
            channel = await self.bot.fetch_channel(
                self.games[str(ctx.guild.id)]["channel"]
            )
            msg = await channel.fetch_message(self.games[str(ctx.guild.id)]["message"])
            print(msg.embeds[0])

            await ctx.followup.send("You have entered the game")

    @atlas.command(name="game-start", description="Start a game of ATLAS")
    async def start(self, ctx):
        await ctx.response.defer()
        if str(ctx.guild.id) not in self.games:
            return await ctx.followup.send(
                embed=dembed(description="No game is currently running")
            )
        elif ctx.channel.id != self.games[str(ctx.guild.id)]["channel"]:
            return await ctx.followup.send(
                embed=dembed(description="This is not the game channel")
            )
        elif len(self.games[str(ctx.guild.id)]["users"]) < 2:
            return await ctx.followup.send(
                embed=dembed(description="Insufficient members for game")
            )
        else:
            self.games[str(ctx.guild.id)]["time"][
                "started"
            ] = ctx.created_at.timestamp()
            order = self.games[str(ctx.guild.id)]["users"].copy()
            original_order = self.games[str(ctx.guild.id)]["users"].copy()
            player_index = 0
            current_alphabet = "S"
            player = await self.bot.fetch_user(order[player_index])
            embed = dembed(
                title="ATLAS Started",
                description=f"{player.mention} Type a place that starts with: **{current_alphabet}**",
                color=theme,
            )
            message = await ctx.followup.send(embed=embed)

            def check(msg):
                return msg.author.id == player.id

            try:
                input = await self.bot.wait_for("message", check=check, timeout=30)
                input_content = input.content.strip().upper()
                check_result = await fetch_data(input_content)
            except asyncio.TimeoutError:
                await ctx.followup.send(
                    embed=dembed(
                        description=f"{player.mention} timed out and has been disqualified"
                    )
                )
                order.remove(player.id)
            else:
                if input.content[0].upper() != current_alphabet:
                    await ctx.followup.send(
                        embed=dembed(
                            description=f"{player.mention} input does not start with the correct letter and has been disqualified"
                        )
                    )
                    order.remove(player.id)
                elif not check_result:
                    await ctx.followup.send(
                        embed=dembed(
                            description=f"{player.mention} entered an invalid place and has been disqualified"
                        )
                    )
                    order.remove(player.id)
                else:
                    current_alphabet = input_content[-1]
                    player_index = (player_index + 1) % len(order)
                    self.games[str(ctx.guild.id)]["places_done"].append(input.content)
                    try:
                        await input.delete()
                    except:
                        pass
                    await message.edit(
                        embed=dembed(
                            title="ATLAS Started",
                            description=f"{player.mention} Type a place that starts with: **{current_alphabet}**",
                            color=theme,
                        )
                    )
            winner = await self.bot.fetch_user(order[0])
            self.games[str(ctx.guild.id)]["time"]["ended"] = ctx.created_at.timestamp()
            game_embed = dembed(
                title="ATLAS Game Details",
                description="Here are the details of the ATLAS game",
                color=theme,
            )
            announce = round(self.games[str(ctx.guild.id)]["time"]["announced"])
            started = round(self.games[str(ctx.guild.id)]["time"]["started"])
            ended = round(self.games[str(ctx.guild.id)]["time"]["ended"])
            player_mentions = [f"<@{user_id}>" for user_id in original_order]
            game_embed.add_field(
                name="Players", value=", ".join(player_mentions), inline=False
            )
            game_embed.add_field(name="Winner", value=f"{winner.mention}", inline=False)
            game_embed.add_field(
                name="Places Done",
                value="\n".join(self.games[str(ctx.guild.id)]["places_done"]),
                inline=False,
            )
            game_embed.add_field(
                name="Announcement Time", value=f"<t:{announce}:F>", inline=False
            )
            game_embed.add_field(
                name="Start Time", value=f"<t:{started}:FF>", inline=False
            )
            game_embed.add_field(name="End Time", value=f"<t:{ended}:R>", inline=False)
            await ctx.followup.send(embed=game_embed)
            del self.games[str(ctx.guild.id)]
            await ctx.followup.send(
                embed=dembed(description=f"Game Ended. The winner is {winner.mention}")
            )


async def setup(bot):
    await bot.add_cog(Atlas(bot))
