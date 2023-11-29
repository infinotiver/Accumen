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

chat_api = os.environ["huggingface"]
chat_url = "https://api-inference.huggingface.co/models/satvikag/chatbot"
headers = {"Authorization": f"Bearer {chat_api}"}


def query(payload):
    response = requests.post(chat_url, headers=headers, json=payload)
    return response.json()


class EduAI(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    group = app_commands.Group(name="eduai", description="artificial intelligence")
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
