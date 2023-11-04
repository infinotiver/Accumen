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

    group = app_commands.Group(name="language", description="Commands related to language")
  
    @group.command(name="grammar", description="Grammar check for your message")
    async def grammar(self, ctx, qtext: str):
      try:
        url = "https://dnaber-languagetool.p.rapidapi.com/v2/check"
        payload = {
          "language": "en",
          "text": qtext
        }
        headers = {
          "content-type": "application/x-www-form-urlencoded",
          "X-RapidAPI-Key": os.environ["rapidapi"],
          "X-RapidAPI-Host": "dnaber-languagetool.p.rapidapi.com"
        }
        response = requests.post(url, data=payload, headers=headers)
        d = response.json()
        matches = d.get("matches", [])  
        # Loop through the 'matches' and print the desired information
        custom_embed=dembed(description="Errors found",color=theme)
        menu = ViewMenu(ctx, menu_type=ViewMenu.TypeEmbedDynamic, rows_requested=1,custom_embed=custom_embed)
        for match in matches:
            message =match["message"]
            description = match["rule"]["description"]
            replacements=[]
            for x in match["replacements"]:
              replacements.append(x["value"])
            replacement=" \n ".join(replacements)
            error_rule = match["rule"]["issueType"]
            error_rule_description=match["rule"]["description"]
            error_category=match["rule"]["category"]["name"]
            offset=match["context"]["offset"]
            length=match["context"]["length"]
            error_context = qtext[offset:offset+length]
            text=f"""
            ## {message}
            ### **Description** :\t {description}
            **Context**:\t ```css\n.{error_context}\n```
            **Replacements** :\t {replacement}
            **Error Rule** :\t {error_rule}
            **Error Rule Description** :\t {error_rule_description}
            **Error Category** :\t {error_category}"""   
            menu.add_row(text)
        main_embed=dembed(title="Grammatical Improvements", description=f" for {qtext}\n Don't rely on me , I can provide incorrect results also.", color=theme)
        menu.set_main_pages(main_embed)
  
        # ViewButton.ID_PREVIOUS_PAGE
        back_button = ViewButton(style=discord.ButtonStyle.primary, label='Back', custom_id=ViewButton.ID_PREVIOUS_PAGE)
        menu.add_button(back_button)
  
        # ViewButton.ID_NEXT_PAGE
        next_button = ViewButton(style=discord.ButtonStyle.secondary, label='Next', custom_id=ViewButton.ID_NEXT_PAGE)
        menu.add_button(next_button)
        await menu.start()
      except:
        await ctx.send(embed=dembed(description="That word doesn't exists.Please check the spellings and try again."))
    @group.command(name="define", description="Define a word from dictionaries")
    async def dictionary(self, ctx, text: str):
      try:
        url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{urllib.parse.quote_plus(text)}"
        response = requests.get(url)
        d = json.loads(response.content)
        embed = dembed(description=f"## {text}")
        phonetics=[]
        for phonetic in d[0]["phonetics"]:
            try:
                phonetics.append(phonetic["text"])
            except:
                pass
        embed.add_field(name="Phonetics",value=", ".join(phonetics))
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
        all_synonyms=[]
        all_antonyms=[]
        for meaning in d[0]["meanings"]:
          for x in meaning.get("synonyms", []):
            all_synonyms.append(x)
          for y in meaning.get("antonyms", []):
            all_antonyms.append(y)
        if len(all_synonyms)>0:
          embed.add_field(
              name="Synonyms", value=", ".join(all_synonyms), inline=False
          )
        if len(all_antonyms)>0:
          embed.add_field(
              name="Antonyms", value=", ".join(all_antonyms), inline=False
          )
        await ctx.response.send_message(embed=embed)
      except:
        await ctx.response.send_message(embed=dembed(description="That word doesn't exists.\nPlease check the spellings and retry"))

async def setup(bot):
    await bot.add_cog(Language(bot))