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
from reactionmenu import ViewMenu, ViewButton
chat_api = os.environ["huggingface"]
chat_url = "https://api-inference.huggingface.co/models/satvikag/chatbot"
headers = {"Authorization": f"Bearer {chat_api}"}


def query(payload):
    response = requests.post(chat_url, headers=headers, json=payload)
    return response.json()
"""
1) title => Essay topic (between 10 to 200 characters)
2) essaytype => Essay Type (['academic', 'narrative', 'argumentative', 'expository', 'descriptive', 'persuasive', 'informative', 'personal-narrative', 'reflective', 'synthesis', 'definition', 'analytical', 'compare-and-contrast', 'cause-and-effect', 'evaluation', 'process'])
3) language => Output language of essay (['english', 'german', 'turkish', 'portuguese', 'spanish', 'russian', 'italian', 'dutch'])
"""

class EduAI(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
    essay_choices = [
        (app_commands.Choice(name="Academic", value='academic')),
        (app_commands.Choice(name="Narrative", value='narrative')),
        (app_commands.Choice(name="Argumentative", value='argumentative')),
        (app_commands.Choice(name="Expository", value='expository')),
        (app_commands.Choice(name="Descriptive", value='descriptive')),
        (app_commands.Choice(name="Persuasive", value='persuasive')),
        (app_commands.Choice(name="Informative", value='informative')),
        (app_commands.Choice(name="Personal-narrative", value='personal-narrative')),
        (app_commands.Choice(name="Reflective", value='reflective')),
        (app_commands.Choice(name="Synthesis", value='synthesis')),
        (app_commands.Choice(name="Definition", value='definition')),
        (app_commands.Choice(name="Analytical", value='analytical')),
        (app_commands.Choice(name="Compare-and-contrast", value='compare-and-contrast')),
        (app_commands.Choice(name="Cause-and-effect", value='cause-and-effect')),
        (app_commands.Choice(name="Evaluation", value='evaluation')),
        (app_commands.Choice(name="Process", value='process'))
       ]
    group = app_commands.Group(name="eduai", description="artificial intelligence")
    @group.command(name="write-essay",description="Currently english only ")
    @app_commands.choices(essay_type=essay_choices)
    @app_commands.describe(title="Describe your subject nicely")
    async def essay(
        self, ctx, title: str,essay_type:app_commands.Choice[str]
    ):
        try:
            await ctx.response.defer()
            url="https://essay-writer.p.rapidapi.com/essay-writer"
            payload = {
              "title": title,
              "essaytype": essay_type.value,
              "language": "english"
            }
            headers = {
                "content-type": "application/json",
                "X-RapidAPI-Key": os.environ["rapidapi"],
                "X-RapidAPI-Host": "essay-writer.p.rapidapi.com"
            }
            response = requests.post(url, json=payload, headers=headers)
            response=response.json()
            essay=response["essay"]
            cites=response["resources"]
            print(essay)
            embed=dembed(title=title,description="API | Hard limit of 8 requests per month ", preset="beta")
            
            max_chars = 1000  # maximum characters per message
            menu = ViewMenu(ctx, menu_type=ViewMenu.TypeEmbedDynamic, rows_requested=1)
            menu.set_main_pages(embed)
            essay_messages = [essay[i:i + max_chars] for i in range(0, len(essay), max_chars)]
            for msg in essay_messages:
                menu.add_row(msg)
            back_button = ViewButton(style=discord.ButtonStyle.primary, label='Back', custom_id=ViewButton.ID_PREVIOUS_PAGE)
            menu.add_button(back_button)
            
            # ViewButton.ID_NEXT_PAGE
            next_button = ViewButton(style=discord.ButtonStyle.secondary, label='Next', custom_id=ViewButton.ID_NEXT_PAGE)
            menu.add_button(next_button)
            await menu.start()
        except Exception as e:
            await ctx.followup.send(f"{e}\nAn error occurred while processing your request.\nThe hard limit of 8 requests per month is applied by the API")
    # Highly fatal , random generations
    @group.command(name="chat", description="Talk to ai")
    async def chat(self, ctx, text: str):
        await ctx.response.defer(ephemeral=True)
        url = "https://ai-chatbot.p.rapidapi.com/chat/free"
        querystring = {"message": text, "uid": ctx.user.id}
        headers = {
            "X-RapidAPI-Key": os.environ["rapidapi"],
            "X-RapidAPI-Host": "ai-chatbot.p.rapidapi.com",
        }
        response = requests.get(url, headers=headers, params=querystring)
        d = response.json()

        await ctx.followup.send(
            embed=dembed(description=d["chatbot"]["response"], preset="beta")
        )


async def setup(bot):
    await bot.add_cog(EduAI(bot))
