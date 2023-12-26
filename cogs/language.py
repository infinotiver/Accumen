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
from reactionmenu import ViewMenu, ViewButton


class Language(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
    language_options = funcs.language_dict
    
    # In the grammar command function
    language_choices = [
        app_commands.Choice(name=lang["name"], value=lang["longCode"]) for lang in language_options
    ]
    group = app_commands.Group(
        name="language", description="Execute language-related commands."
    )

    @group.command(name="grammar")
    @app_commands.choices(language=language_choices)
    @app_commands.describe(query_text="The message to check for grammar errors.")
    async def grammar(self, ctx, query_text: str,*,language:app_commands.Choice[str]):
        await ctx.response.defer()
        try:
            if not language:
              language.value="en"
            url = "https://dnaber-languagetool.p.rapidapi.com/v2/check"
            payload = {"language": language.value, "text": query_text}
            headers = {
                "content-type": "application/x-www-form-urlencoded",
                "X-RapidAPI-Key": os.environ["rapidapi"],
                "X-RapidAPI-Host": "dnaber-languagetool.p.rapidapi.com",
            }
            response = requests.post(url, data=payload, headers=headers)
            d = response.json()
            matches = d.get("matches", [])
            custom_embed = dembed(description="Errors Found", color=theme)
            menu = ViewMenu(
                ctx,
                menu_type=ViewMenu.TypeEmbedDynamic,
                rows_requested=1,
                custom_embed=custom_embed,
            )
            for match in matches:
                message = match.get("message")
                description = match["rule"]["description"]
                replacements = [x["value"] for x in match["replacements"]]
                replacement = "\n".join(replacements)
                error_rule = match["rule"]["issueType"]
                error_rule_description = match["rule"]["description"]
                error_category = match["rule"]["category"]["name"]
                offset = match["context"]["offset"]
                length = match["context"]["length"]
                error_context = query_text[offset: offset + length]
                text = f"""
            ## {message}
            ### **Description** : {description}
            **Context**: ```css\n.{error_context}\n```
            **Replacements**: {replacement}
            **Error Rule**: {error_rule}
            **Error Rule Description**: {error_rule_description}
            **Error Category**: {error_category}"""
                menu.add_row(text)

            main_embed = dembed(
                title="Grammatical Improvements",
                description=f" for {query_text}\n Please note that I may provide incorrect results as well.",
            )
            menu.set_main_pages(main_embed)

            back_button = ViewButton(
                style=discord.ButtonStyle.primary,
                label="Back",
                custom_id=ViewButton.ID_PREVIOUS_PAGE,
            )
            menu.add_button(back_button)

            next_button = ViewButton(
                style=discord.ButtonStyle.secondary,
                label="Next",
                custom_id=ViewButton.ID_NEXT_PAGE,
            )
            menu.add_button(next_button)

            await menu.start()

        except:
            await ctx.followup.send(
                embed=dembed(
                    description="The word does not exist. Please check the spelling and try again."
                )
            )

    @group.command(name="define")
    @app_commands.describe(text="The word to define.")
    async def dictionary(self, ctx, text: str):
        await ctx.response.defer()
        try:
            url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{urllib.parse.quote_plus(text)}"
            response = requests.get(url)
            d = json.loads(response.content)
            embed = dembed(description=f"## {text}")
            phonetics = []
            for phonetic in d[0]["phonetics"]:
                try:
                    phonetics.append(phonetic["text"])
                except:
                    pass
            embed.add_field(name="Phonetics", value=", ".join(phonetics))

            for meaning in d[0]["meanings"]:
                field_value = ""
                for definition in meaning["definitions"]:
                    try:
                        definition_text = definition["definition"]
                        definition_parts = [
                            definition_text[i: i + 1000]
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

            all_synonyms = [x for meaning in d[0]["meanings"] for x in meaning.get("synonyms", [])]
            all_antonyms = [y for meaning in d[0]["meanings"] for y in meaning.get("antonyms", [])]

            if all_synonyms:
                embed.add_field(
                    name="Synonyms", value=", ".join(all_synonyms), inline=False
                )
            if all_antonyms:
                embed.add_field(
                    name="Antonyms", value=", ".join(all_antonyms), inline=False
                )

            await ctx.followup.send(embed=embed)
            
        except:
            await ctx.followup.send(
                embed=dembed(
                    description="The word does not exist. Please check the spelling and try again."
                )
            )


async def setup(bot):
    await bot.add_cog(Language(bot))