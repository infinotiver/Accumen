import datetime
import os
import time
import utils.functions as funcs
from utils.functions import dembed, theme, divider
import discord
import motor.motor_asyncio
import nest_asyncio
import requests
from discord.ext import commands, tasks, timers
from discord.ext.commands import BucketType, cooldown
from pymongo import MongoClient
from discord import app_commands

nest_asyncio.apply()
mongo_url = os.environ["mongodb"]
cluster = motor.motor_asyncio.AsyncIOMotorClient(mongo_url)
reminder = cluster["accumen"]["reminder"]


class Remind(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.checker.start()

    group = app_commands.Group(name="remind", description="Reminders")

    @commands.Cog.listener()
    async def on_ready(self):
        print("Remind cog loaded successfully")

    @group.command(name="notify")
    @cooldown(1, 30, BucketType.user)
    async def notify(self, ctx, ttime: str, *, desc: str):
        try:
            if "every" in ttime:
                ttime_parts = ttime.split("every")
                print(ttime_parts)
                if len(ttime_parts) < 2:
                    await ctx.response.send_message("**Invalid time format**")
                    return
                ttime = ttime_parts[1].strip()
                print(ttime)
                typ = ttime[-1]
                ttime = int(ttime[0:-1])
                choices = ["s", "m", "h", "d"]
                if typ not in choices:
                    await ctx.response.send_message(
                        "**Only s(seconds), m(minutes),h(hours),d(days)**"
                    )
                else:
                    if typ == "s":
                        conv = ttime
                    elif typ == "m":
                        conv = ttime * 60
                    elif typ == "h":
                        conv = ttime * 3600
                    elif typ == "d":
                        conv = ttime * 86400

                    if conv > 604800:
                        await ctx.response.send_message("**Not more than 7 days**")
                    else:
                        await ctx.response.send_message("**Reminder has been set**")
                        a = datetime.datetime.now()
                        a = a + datetime.timedelta(seconds=conv)
                        newuser = {
                            "id": ctx.user.mention,
                            "Time": a,
                            "Desc": desc,
                            "Channel": ctx.channel.id,
                            "Every": ttime,
                        }
                        await reminder.insert_one(newuser)
            else:
                if len(desc) < 50:
                    typ = ttime[-1]
                    ttime = int(ttime[0:-1])
                    choices = ["s", "m", "h", "d"]
                    if typ not in choices:
                        await ctx.response.send_message(
                            "**Only s(seconds), m(minutes),h(hours),d(days)**"
                        )
                    else:
                        if typ == "s":
                            conv = ttime
                        elif typ == "m":
                            conv = ttime * 60
                        elif typ == "h":
                            conv = ttime * 3600
                        elif typ == "d":
                            conv = ttime * 86400

                        if conv > 604800:
                            await ctx.response.send_message("**Not more than 7 days**")
                        else:
                            await ctx.response.send_message("**Reminder has been set**")
                            a = datetime.datetime.now()
                            a = a + datetime.timedelta(seconds=conv)
                            newuser = {
                                "id": str(ctx.user.id),
                                "Time": a,
                                "Desc": desc,
                                "Channel": ctx.channel.id,
                            }
                            await reminder.insert_one(newuser)

                else:
                    await ctx.response.send_message("**Too Long Reminder**")
        except ValueError:
            pass

    @tasks.loop(seconds=10)
    async def checker(self):
        try:
            all_reminders = reminder.find({})
            current_time = datetime.datetime.now()

            for reminder_doc in await all_reminders.to_list(length=None):
                reminder_time = reminder_doc["Time"]
                channel_id = reminder_doc["Channel"]
                desc = reminder_doc["Desc"]
                person = reminder_doc["id"]

                if current_time >= reminder_time:
                    channel = self.client.get_channel(channel_id)
                    embed = discord.Embed(
                        title="Reminder", description=desc, color=funcs.theme
                    )
                    embed.set_footer(text=f"Set by {person}")
                    await channel.send(embed=embed)

                    # Check if the reminder is recurring
                    every_time = reminder_doc.get("Every")
                    if every_time:
                        new_time = reminder_time + datetime.timedelta(
                            seconds=every_time
                        )
                        await reminder.update_one(
                            {"_id": reminder_doc["_id"]}, {"$set": {"Time": new_time}}
                        )
                    else:
                        await reminder.delete_one(reminder_doc)
        except Exception as e:
            print(f"Error in checker task: {e}")

    @group.command()
    async def showreminders(self, ctx):
        all_reminders = reminder.find({"id": str(ctx.user.id)})
        embed = dembed(title="Your Reminders")
        async for x in all_reminders:
            desc = x["Desc"]
            time = x["Time"].strftime("%Y-%m-%d %I:%M %p")
            embed.add_field(
                name="Reminder", value=f"**{desc}**\nSet for: {time}", inline=False
            )
        if len(embed.fields) > 0:
            await ctx.response.send_message(embed=embed)
        else:
            await ctx.response.send_message("You have no reminders set.")


async def setup(bot):
    await bot.add_cog(Remind(bot))
