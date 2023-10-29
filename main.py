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

intents = discord.Intents.all()
client = commands.Bot(command_prefix="a!", intents=intents)
# client = app_commands.Commandclient(client)


@client.event
async def on_ready():
  os.system("clear")

  font = Figlet(font="standard")
  print(colored(font.renderText(client.user.name), "blue"))
  print(
    colored(f"[+] Logged in as {client.user} (ID: {client.user.id})", "blue"))
  print(colored(f"[+] Connecited to {len(client.guilds)} servers", "blue"))
  print(colored(f"[+] Serving {len(client.users)} users", "blue"))
  print(
    colored(
      f"[+] Memory usage: {psutil.Process().memory_info().rss / 1024 ** 2:.2f} MB",
      "light_blue",
    ))
  for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
      try:
        await client.load_extension(f"cogs.{filename[:-3]}")
        print(colored(f"[+] Loaded {filename}", "green"))
      except Exception as e:
        print(colored(f"[-] Not Loaded {filename}\n {e}", "red"))
  print(colored("[+] All available cogs loaded", "green"))
  # Send an initial message to a specific channel on startup
  channel = client.get_channel(
    953571969780023366)  # Replace with your channel ID
  system_latency = round(client.latency * 1000)
  em = dembed(title=f"{client.user.name} Online!", description="I'm Up")
  em.set_thumbnail(url=client.user.avatar.url)
  em.add_field(name="Ping", value=f"{system_latency} ms", inline=False)
  em.add_field(name="Servers", value=f"{len(client.guilds)}", inline=True)
  em.add_field(name="Users", value=f"{len(client.users)}", inline=True)
  await channel.send(embed=em)
  client.add_view(ubuttons.Qrscontrol())
  print(colored(f"[+] Persistent View (Queries)", "blue"))
  await client.tree.sync()


@app_commands.command(name="hi")
async def hello(interaction: discord.Interaction):
  """Says hello!"""
  await interaction.response.send_message(f"Hi, {interaction.user.mention}")


keep_alive()

client.run(os.environ["token"], reconnect=True)
