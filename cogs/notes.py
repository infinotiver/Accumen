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
notedb = cluster["accumen"]["note"]
categories = {
    "Important": "important",
    "Work": "work",
    "Personal": "personal",
    "Others": "others",
}


class SelfNotes(commands.Cog):
    def __init__(self, client):
        self.client = client

    notes = app_commands.Group(name="notes", description="Notes")

    @commands.Cog.listener()
    async def on_ready(self):
        print("Note cog loaded successfully")

    @notes.command(name="view", description="Shows your saved notes")
    async def view(self, ctx):
        notes = await notedb.find({"id": ctx.user.id}).to_list(length=None)

        if not notes:
            embed = dembed(
                timestamp=ctx.message.created_at,
                title="Notes",
                description=f"{ctx.user.mention} has no saved notes yet...",
            )
            await ctx.followup.send(embed=embed)
            return

        embed = dembed(
            title="Your Notes",
            description="Here are your notes",
        )
        for note in notes:
            category = note["category"]
            message = note["note"]
            embed.add_field(name=category, value=message, inline=False)

        await ctx.user.send(embed=embed)
        await ctx.followup.send(
            embed=dembed(
                description=f"{ctx.user.mention}, I have sent your notes to your DM!"
            )
        )

    @notes.command(name="add", description="Adds a note to the selected category")
    @app_commands.choices(
        category=[
            app_commands.Choice(name=name, value=value)
            for name, value in categories.items()
        ]
    )
    async def add(self, ctx, *, message: str, category: app_commands.Choice[str]):
        await ctx.response.defer(ephemeral=False)
        message = str(message)
        new_note = {"id": ctx.user.id, "category": category.value, "note": message}
        notedb.insert_one(new_note)

        embed = dembed(
            title="New Note",
            description="**<:note:942777255376068659>Your note has been stored**",
        )
        await ctx.followup.send(embed=embed)

    @notes.command(name="delete", description="Deletes a note")
    async def delete(self, ctx, note_id: int):
        await ctx.response.defer(ephemeral=False)
        notes = await notedb.find({"id": ctx.user.id}).to_list(length=None)

        if note_id > 0 and note_id <= len(notes):
            note = notes[note_id - 1]
            category = note["category"]
            message = note["note"]

            await notedb.delete_one(note)

            embed = dembed(
                title="Note Deleted",
                description=f"**Deleted note from category `{category}`:**\n{message}",
            )
            await ctx.followup.send(embed=embed)
        else:
            await ctx.followup.send(embed=dembed(description="Invalid note ID."))

    @notes.command(name="categories", description="Shows available categories")
    async def categories(self, ctx):
        await ctx.response.defer(ephemeral=False)
        embed = dembed(
            title="Available Categories",
            description="Here are the available categories",
        )
        for index, category in enumerate(self.categories, start=1):
            embed.add_field(name=f"Category {index}", value=category, inline=False)

        await ctx.followup.send(embed=embed)


async def setup(bot):
    await bot.add_cog(SelfNotes(bot))
