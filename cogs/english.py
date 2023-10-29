import discord
import json
from discord.ext import commands
import utils.calc as calc
from discord import app_commands
import requests
import os
import json
import utils.functions as funcs
from utils.functions import dembed, theme, divider
import urllib.parse


class English(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    group = app_commands.Group(name="english", description="English")

    @group.command(name="grammar", description="Grammar check for your message")
    async def grammar(self, ctx, text: str):
        url = "https://dnaber-languagetool.p.rapidapi.com/v2/check"
        payload = f"text={urllib.parse.quote_plus(text)}&language=en-US"
        headers = {
            "content-type": "application/x-www-form-urlencoded",
            "X-RapidAPI-Key": os.environ["rapidapi"],
            "X-RapidAPI-Host": "dnaber-languagetool.p.rapidapi.com",
        }
        response = requests.request("POST", url, data=payload, headers=headers)
        d = json.loads(response.content)
        # print(d)
        matches = d["matches"]
        message = "**Grammar check results\n**"
        embed = dembed(title=message)
        for match in matches:
            message = f"**- {match['message']} ({match['rule']['description']})**\n"
            if match["replacements"]:
                message += f"\n\tSuggested replacements:** {', '.join([rep['value'] for rep in match['replacements']])}**"
            message += f"\n\tContext:\n > {match['context']['text']}"
            embed.add_field(name="_ _", value=message, inline=False)
        await ctx.response.send_message(embed=embed)

    @group.command(name="dictionary", description="Define a word")
    async def dictionary(self, ctx, text: str):
        url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{urllib.parse.quote_plus(text)}"
        response = requests.get(url)
        d = json.loads(response.content)
        embed = dembed(title=text)
        for phonetic in d[0]["phonetics"]:
            try:
                embed.add_field(name="Phonetic", value=phonetic["text"], inline=False)
            except:
                pass

        # add meanings
        for meaning in d[0]["meanings"]:
            field_value = ""
            for definition in meaning["definitions"]:
                try:
                    definition_text = definition["definition"]
                    # split definition into smaller parts
                    definition_parts = [
                        definition_text[i : i + 1000]
                        for i in range(0, len(definition_text), 1000)
                    ]
                    for part in definition_parts:
                        field_value += f"- {part}\n"
                except:
                    pass
            if field_value:
                embed.add_field(
                    name=meaning["partOfSpeech"], value=field_value, inline=False
                )

        await ctx.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(English(bot))
