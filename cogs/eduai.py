import json
import discord
from discord.ext import commands
from discord import app_commands
import requests
import os
from utils.functions import dembed

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
        (app_commands.Choice(name="Academic", value="academic")),
        (app_commands.Choice(name="Narrative", value="narrative")),
        (app_commands.Choice(name="Argumentative", value="argumentative")),
        (app_commands.Choice(name="Expository", value="expository")),
        (app_commands.Choice(name="Descriptive", value="descriptive")),
        (app_commands.Choice(name="Persuasive", value="persuasive")),
        (app_commands.Choice(name="Informative", value="informative")),
        (app_commands.Choice(name="Personal-narrative", value="personal-narrative")),
        (app_commands.Choice(name="Reflective", value="reflective")),
        (app_commands.Choice(name="Synthesis", value="synthesis")),
        (app_commands.Choice(name="Definition", value="definition")),
        (app_commands.Choice(name="Analytical", value="analytical")),
        (
            app_commands.Choice(
                name="Compare-and-contrast", value="compare-and-contrast"
            )
        ),
        (app_commands.Choice(name="Cause-and-effect", value="cause-and-effect")),
        (app_commands.Choice(name="Evaluation", value="evaluation")),
        (app_commands.Choice(name="Process", value="process")),
    ]
    group = app_commands.Group(name="eduai", description="artificial intelligence")

    @group.command(name="write-essay", description="Currently english only ")
    @app_commands.choices(essay_type=essay_choices)
    @app_commands.describe(title="Describe your subject nicely")
    async def essay(self, ctx, title: str, essay_type: app_commands.Choice[str]):
        return await ctx.response.send_message(
            embed=dembed(
                title="Command Unavailable",
                description="This command is currently under maintenance and not available for use.",
                preset="beta",
            )
        )

    # Highly fatal , random generations
    @group.command(
        name="chat", description="[EXPERIMENTAL] [BETA] Talk to A.I. chatbot"
    )
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
