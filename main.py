from typing import Optional
import os
import discord
from discord import app_commands
from discord.ext import commands
import utils.functions as funcs
from termcolor import colored
from pyfiglet import Figlet
import urllib, re
import wikipedia
import psutil
import utils.functions as funcs
from utils.functions import dembed, theme, divider
from keeplive import keep_alive
import utils.buttons as ubuttons
import motor.motor_asyncio
import nest_asyncio
import typing
import asyncio

intents = discord.Intents.all()
client = commands.Bot(command_prefix="a!", intents=intents)
mongo_url = os.environ["mongodb"]
cluster = motor.motor_asyncio.AsyncIOMotorClient(mongo_url)
incoming = cluster["accumen"]["incoming"]


@client.event
async def on_ready():
    os.system("clear")
    font = Figlet(font="standard")
    print(colored(font.renderText(client.user.name), "blue"))
    print(colored(f"[+] Signed in as {client.user} (ID: {client.user.id})", "blue"))
    print(colored(f"[+] Connected to {len(client.guilds)} servers", "blue"))
    print(colored(f"[+] Available to {len(client.users)} users", "blue"))
    print(
        colored(
            f"[+] Memory usage: {psutil.Process().memory_info().rss / 1024 ** 2:.2f} MB",
            "light_blue",
        )
    )
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            try:
                await client.load_extension(f"cogs.{filename[:-3]}")
                print(colored(f"[+] {filename}", "light_green"))
            except Exception as e:
                print(colored(f"[-] Not Loaded {filename}\n {e}", "red"))
    print(colored("[+] All stable cogs loaded", "blue"))
    channel = client.get_channel(1197514010388611102)  
    system_latency = round(client.latency * 1000)
    em = dembed(title=f"{client.user.name} is online !")
    em.set_thumbnail(url=client.user.avatar.url)
    em.add_field(name="Ping", value=f"{system_latency} ms", inline=False)
    em.add_field(name="Servers", value=f"{len(client.guilds)}", inline=True)
    em.add_field(name="Users", value=f"{len(client.users)}", inline=True)
    await channel.send(embed=em)
    client.add_dynamic_items(ubuttons.dynamic_add_answer)
    client.add_dynamic_items(ubuttons.dynamic_upvote)
    client.add_dynamic_items(ubuttons.dynamic_report)
    client.add_view(ubuttons.answercontrol())
    print(colored("[+] Persistent views and Dynamic items ", "light_blue"))
    await client.tree.sync()

# Add credit and thanks for hosting
keep_alive()
client.run(os.environ["token"], reconnect=True)
