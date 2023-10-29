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

    @group.command(name="chat", description="talk to ai")
    async def chat(self, ctx, text: str, time: int = None):
        await ctx.response.defer(ephemeral=True)
        if not time:
            time = 10
        url = "https://you-chat-gpt.p.rapidapi.com/"
        payload = {"question": text, "max_response_time": time}
        headers = {
            "content-type": "application/json",
            "X-RapidAPI-Key": os.environ["rapidapi"],
            "X-RapidAPI-Host": "you-chat-gpt.p.rapidapi.com",
        }
        response = requests.request("POST", url, json=payload, headers=headers)
        d = json.loads(response.content)
        # print(d["answer"])
        await ctx.followup.send(embed=dembed(description=d["answer"], preset="beta"))

    @group.command(name="gen", description="generate")
    async def text2img(self, ctx, *, text: str):
        await ctx.response.defer(ephemeral=True)
        chat = query(
            {
                "inputs": {
                    "past_user_inputs": [],
                    "generated_responses": [],
                    "text": text,
                },
                "wait_for_model": True,
            }
        )
        print(chat)
        await ctx.followup.send(
            embed=dembed(
                description=chat["generated_text"],
                preset="beta",
                footer="Doesnt saves past input as of now... Responses can be wild \n Using 3rd Party Extension",
            )
        )


async def setup(bot):
    await bot.add_cog(EduAI(bot))
