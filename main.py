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
import datetime
import time
intents = discord.Intents.all()
client = commands.Bot(command_prefix="a!", intents=intents,owner_id=900992402356043806)
mongo_url = os.environ.get("mongodb")
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

    system_latency = round(client.latency * 1000)
    view=ubuttons.contro()
    em = dembed(title=f"{client.user.name} is online !")
    em.set_thumbnail(url=client.user.avatar.url)
    em.add_field(name="Ping", value=f"{system_latency} ms", inline=False)
    em.add_field(name="Servers", value=f"{len(client.guilds)}", inline=True)
    last_server_count=len(client.guilds)
    em.add_field(name="Users", value=f"{len(client.users)}", inline=True)
    channel=client.get_channel(1197514010388611102)
    await channel.purge(limit=100) 
    msg=await channel.send(embed=em,view=view)
    client.add_dynamic_items(ubuttons.dynamic_add_answer)
    client.add_dynamic_items(ubuttons.dynamic_upvote)
    client.add_dynamic_items(ubuttons.dynamic_report)
    client.add_view(ubuttons.answercontrol())
    print(colored("[+] Persistent views and Dynamic items ", "light_blue"))
    GUILDID =976878887004962917 

    await client.tree.sync(guild=discord.Object(GUILDID))
    await client.tree.sync()
    while True:
      await asyncio.sleep(300)
      current_server_count=len(client.guilds)
      change=current_server_count-last_server_count
      last_server_count=current_server_count
      em.set_field_at(index=1, name="Servers", value=f"{len(client.guilds)} ({change})")
      ctime=datetime.datetime.now()
      unixtime = time.mktime(ctime.timetuple())
      em.description=f"\n last updated <t:{int(unixtime)}:R>"
      em.set_footer(text=f"Last Updated {ctime}")
      await msg.edit(embed=em,view=view)


client.run(os.environ.get("token"), reconnect=True)

# Trying something