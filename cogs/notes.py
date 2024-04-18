import os
import asyncio
import discord
from discord.ext import commands
from discord import Button, SelectMenu, SelectOption
from pymongo import MongoClient
from discord import app_commands
import utils.buttons
import utils.functions as funcs
from utils.functions import dembed, theme, divider

mongo_url = os.environ["mongodb"]
cluster = MongoClient(mongo_url)
notes_mongodb = cluster["accumen"]["note"]

categories = {
    "Important": "important",
    "Work": "work",
    "Personal": "personal",
    "Others": "others",
}


class SelfNotes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Note cog loaded successfully")

    async def send_embed(self, ctx, title: str, description: str):
        embed = dembed(title=title, description=description)
        await ctx.followup.send(embed=embed)

    notes = app_commands.Group(
        name="notes", description="Store your most important stuff and (maybe) secrets"
    )

    @notes.command(name="view", description="Shows your saved notes")
    async def view(self, ctx):
        await ctx.response.defer(ephemeral=True)
        notes_cursor = await notes_mongodb.find({"id": ctx.user.id}).to_list(None)
        notes = []
        async for note in notes_cursor:
            notes.append(note)
        if not notes:
            await ctx.followup.send(
                "Notes", f"{ctx.user.mention} has no saved notes yet..."
            )
            return

        embed = dembed(title="Your Notes", description="Here are your notes")
        for note in notes:
            category = note["category"]
            message = note["note"]
            embed.add_field(name=category, value=message, inline=False)

        await ctx.followup.send(embed=embed, ephemeral=True)

    @notes.command(name="add", description="Adds a note to the selected category")
    @app_commands.choices(
        category=[
            app_commands.Choice(name=name, value=value)
            for name, value in categories.items()
        ]
    )
    async def add(self, ctx, message: str, category: app_commands.Choice[str]):
        await ctx.response.defer(ephemeral=True)
        category = category.value

        new_note = {"id": ctx.user.id, "category": category, "note": message}
        notes_mongodb.insert_one(new_note)

        await ctx.followup.send(
            embed=dembed(title="New Note", description="Your note has been stored.")
        )

    @notes.command(name="delete", description="Deletes a note")
    async def delete(self, ctx, note_id: int):
        await ctx.response.defer(ephemeral=True)
        notes_cursor = await notes_mongodb.find({"id": ctx.user.id})
        notes = await notes_cursor.to_list(length=None)
        if 0 < note_id <= len(notes):
            note = notes[note_id - 1]
            category = note["category"]
            message = note["note"]

            await notes_mongodb.delete_one(note)

            await ctx.followup.send(
                embed=dembed(
                    title="Note Deleted",
                    description=f"Deleted note from category `{category}`:\n{message}",
                )
            )
        else:
            await ctx.followup.send("Invalid Note ID")


"""
    @notes.command(name="categories", description="Shows available categories")
    async def categories(self, ctx):
        await ctx.response.defer(ephemeral=True)

        embed = dembed(title="Available Categories", description="Here are the available categories")
        for index, category in enumerate(categories, start=1):
            embed.add_field(name=f"Category {index}", value=category, inline=False)

        await ctx.followup.send(embed=embed)
"""


async def setup(bot):
    await bot.add_cog(SelfNotes(bot))
