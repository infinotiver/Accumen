import discord
import json
from discord.ext import commands
from discord import app_commands
import requests
import os
import json
import utils.functions as funcs
from utils.functions import dembed, theme, divider
from discord.utils import format_dt
import motor.motor_asyncio
import nest_asyncio
import typing
import asyncio
from reactionmenu import ViewMenu, ViewButton
import utils.buttons as assetsb

nest_asyncio.apply()

mongo_url = os.environ["mongodb"]

cluster = motor.motor_asyncio.AsyncIOMotorClient(mongo_url)
queries_col = cluster["accumen"]["queries"]
incoming = cluster["accumen"]["incoming"]
# esult = queries_col.delete_many({})
# print("documents deleted.")
SUBJECTS = {
    "English Language": "english_language",
    "English Literature": "english_literature",
    "Mathematics": "mathematics",
    "Biology": "biology",
    "Chemistry": "chemistry",
    "Physics": "physics",
    "History": "history",
    "Geography": "geography",
    "Computer Science": "computer_science",
    "Fine Arts": "fine_arts",
    "Economics": "economics",
    "Foreign Languages": "foreign_languages",
    "Physical Education": "physical_education",
    "Health Science": "health_science",
    "Law": "law",
    "Media Studies": "media_studies",
    "Other": "other",
}
EDUCATION_LEVELS = {
    "Primary School": "1",
    "Middle School": "2",
    "High School": "3",
    "Undergraduate": "4",
    "Postgraduate": "5",
    "Doctorate": "6",
}
# Define a list comprehension to create the subject choices
subject_choices = [
    app_commands.Choice(name=name, value=value) for name, value in SUBJECTS.items()
]

# Define a list comprehension to create the education level choices
education_level_choices = [
    app_commands.Choice(name=name, value=value)
    for name, value in EDUCATION_LEVELS.items()
]


async def get_filtered_queries(category=None, difficulty=None):
    query_filter = {}
    if category:
        query_filter["category"] = category
    if difficulty:
        query_filter["difficulty"] = difficulty
    queries_cursor = queries_col.find(query_filter)
    queries = []
    async for query in queries_cursor:
        queries.append(query)
    return queries


class Assist(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    group = app_commands.Group(name="query", description="Query Ask")

    async def query_autocompletion(
        interaction: discord.Interaction, current: str, option: bool = False
    ) -> typing.List[app_commands.Choice[str]]:
        data = []
        queries_cursor = queries_col.to_list(length=None)
        queries = []
        async for query in queries_cursor:
            queries.append(query)

        for query in queries:
            print(query)
            title_words = query["title"].split()
            print(f"Title {title_words[0]}")

            for word in title_words:
                if current.text.lower() == word.lower():
                    data.append(
                        discord.Choice(label=query["title"], value=query["_id"])
                    )
                    break
        return data

    @group.command(
        name="post",
        description="Ask to People.Post your query here and get answers from all the servers ",
    )
    @app_commands.choices(
        category=[
            app_commands.Choice(name=name, value=value)
            for name, value in SUBJECTS.items()
        ]
    )
    @app_commands.choices(
        diffi=[
            app_commands.Choice(name=name, value=value)
            for name, value in EDUCATION_LEVELS.items()
        ]
    )
    async def pt(
        self,
        ctx,
        category: app_commands.Choice[str],
        diffi: app_commands.Choice[str],
        title: str,
        description: str,
    ):
        await ctx.response.defer(ephemeral=False)
        id = funcs.generate_query_id(title, description)
        query = {
            "_id": id,
            "user_id": ctx.user.id,
            "category": category.value,
            "difficulty": diffi.value,
            "title": title,
            "description": description,
            "timestamp": ctx.created_at.timestamp(),
            "guild_id": ctx.guild.id,
            "votes": 0,
            "voted_users": [],
            "messages": [],
            "closed": False,
        }
        # Insert the query into the queries collection
        await queries_col.insert_one(query)
        embed = discord.Embed(title=f"**{title}**", color=theme)
        authr = f"{str(ctx.user.display_name)} ∙ {diffi.name}"
        embed.set_author(name=authr, icon_url=ctx.user.avatar.url)
        embed.add_field(name="Votes", value="0")
        embed.add_field(name="Category", value=f"`{category.name}`")
        embed.add_field(name="Answer", value="`10`points")
        timestamp = format_dt(ctx.created_at, "R")
        des = f"**{id}** ∙ Posted in {ctx.guild.name} , {timestamp}\n{divider}\n **{description}**"
        embed.description = des
        sent = dembed(
            title="Query Submitted",
            description="Keep your dm open",
            color=funcs.secondary_theme,
        )
        sent.add_field(name="Query", value=description, inline=False)
        omsg = await ctx.followup.send(embed=sent)
        data = await incoming.find().to_list(length=None)
        for x in data:
            guild = await self.bot.fetch_guild(int(x["_id"]))
            channel = self.bot.get_channel(int(x["channel"]))

            view = assetsb.Qrscontrol()
            #          self.bot.add_view(view())
            view.add_item(
                discord.ui.Button(
                    label="Community",
                    style=discord.ButtonStyle.link,
                    url="https://discord.gg/Nvts32BAwr",
                )
            )
            msg = await channel.send(content="New Query", embed=embed, view=view)

            fq = await queries_col.find_one({"_id": id})
            fq["messages"].append(
                {"channel": str(channel.id), "msg": msg.id, "guild": str(guild.id)}
            )
            await queries_col.replace_one({"_id": id}, fq)
            view.message = msg

        oview = discord.ui.View(timeout=None)
        oview.add_item(
            discord.ui.Button(
                label="Successfuly Posted",
                style=discord.ButtonStyle.primary,
                disabled=True,
            )
        )
        await omsg.edit(embed=sent, view=oview)

    @group.command(name="answer", description="Answer ")
    @app_commands.autocomplete(query_id=query_autocompletion)
    async def answer_query(self, ctx, query_id: str, answer: str):
        await ctx.response.defer(ephemeral=False)
        # Find the query in the database
        query = await queries_col.find_one({"_id": query_id})

        if not query:
            await ctx.followup.send(f"Query with ID {query_id} not found.")
            return
        user_id = ctx.user.id
        for answer in query.get("answers", []):
            if answer.get("user") == user_id:
                await ctx.followup.send("You have already answered this query.")
                return
        # Add the answer to the query document
        if "answers" not in query:
            query["answers"] = []

        user_id = ctx.user.id
        query["answers"].append({"ans": answer, "user": user_id})

        # Update the query in the database
        result = await queries_col.replace_one({"_id": query_id}, query)

        if result.modified_count == 0:
            await ctx.followup.send("Failed to update query.")
            return

        # Get the original answerer's user ID
        des = f"Posted on {ctx.guild.name}\n{divider}\n Query ID: {query_id}\nAnswer: {answer}"
        original_answerer_id = query.get("user_id")
        embed = dembed(title="New Answer", description=des, color=theme)
        embed.set_author(name=ctx.user.name, icon_url=ctx.user.avatar.url)
        await ctx.followup.send("Answered Query...")
        # Send a DM to the original answerer with the new answer
        if original_answerer_id:
            # Fetch the original answerer and create a view with two buttons
            original_answerer = await self.bot.fetch_user(original_answerer_id)
            message = await original_answerer.send("New Answer 📩", embed=embed)

    @group.command(name="list", description="Checkout")
    # @commands.has_permissions(manage_messages=True)
    async def listset(self, ctx):
        await ctx.response.defer()
        queries_cursor = queries_col.find()
        queries = []
        async for query in queries_cursor:
            queries.append(query)
        print(queries)
        menu = ViewMenu(
            ctx,
            menu_type=ViewMenu.TypeEmbedDynamic,
            rows_requested=1,
            custom_embed=dembed(title="All Queries on Accumen"),
        )
        for x in queries:
            id = x["_id"]
            title = x["title"]
            desc = x["description"]
            time = round(x["timestamp"])
            category = x["category"]
            difficulty = x["difficulty"]
            guild = await self.bot.fetch_guild(x["guild_id"])
            closed = x["closed"]
            status = (
                "<:Y1:1045710123739381841> Yes"
                if not closed
                else "<:N1:1045709774785875998> No"
            )
            # Get the total number of answers
            num_answers = len(query.get("answers", []))

            # Get the list of answers
            answers_list = []
            for answer in query.get("answers", []):
                answer_text = answer["ans"]
                answer_user = self.bot.fetch_user(answer["user"])
                answers_list.append(f"{answer_text} by {answer_user.name}")
            # Format the description string with all the available information
            des = f"**ID:** {id}\n**Title:** {title}\n**Description:** {desc}\n**Category:** {category}\n**Difficulty:** {difficulty}\n**Created:** <t:{time}:R>\n**Guild:** {guild.name}\n**Open:** {status}\n**Total Answers:** {num_answers}\n**Answers:** {', '.join(answers_list) if answers_list else 'None'}\n{divider}"
            menu.add_row(des)

        # ViewButton.ID_PREVIOUS_PAGE
        back_button = ViewButton(
            style=discord.ButtonStyle.primary,
            label="Back",
            custom_id=ViewButton.ID_PREVIOUS_PAGE,
        )
        menu.add_button(back_button)

        # ViewButton.ID_NEXT_PAGE
        next_button = ViewButton(
            style=discord.ButtonStyle.secondary,
            label="Next",
            custom_id=ViewButton.ID_NEXT_PAGE,
        )
        menu.add_button(next_button)
        await menu.start()

    @group.command(
        name="incoming", description="Set channel where you recieve all the queries"
    )
    @commands.has_permissions(manage_messages=True)
    async def incomingset(self, ctx, channel: discord.TextChannel):
        await ctx.response.defer()
        results = await incoming.find_one({"_id": ctx.guild.id})
        if not results:
            query = {"_id": ctx.guild.id, "channel": channel.id}
            await incoming.insert_one(query)

        else:
            await incoming.update_one(
                {"_id": ctx.guild.id}, {"$set": {"channel": channel.id}}
            )
        await ctx.followup.send(
            embed=dembed(
                description=f"Successfuly Set Incoming  Channel \t {channel.mention}"
            )
        )

    @group.command(name="dashboard", description="Access the query dashboard")
    async def dashboard(self, ctx):
        await ctx.response.defer()

        # Fetch all queries from the database
        queries_cursor = queries_col.find()
        queries = []
        async for query in queries_cursor:
            queries.append(query)

        # Create a list of query IDs for easy reference
        query_ids = [query["_id"] for query in queries]

        # Create a dictionary to store the query data
        query_data = {}

        # Iterate over each query and store the relevant data
        for query in queries:
            if query["user_id"] == ctx.user.id:
                query_id = query["_id"]
                title = query["title"]
                description = query["description"]
                category = query["category"]
                difficulty = query["difficulty"]
                closed = query["closed"]

                # Store the query data in the dictionary
                query_data[query_id] = {
                    "title": title,
                    "description": description,
                    "category": category,
                    "difficulty": difficulty,
                    "closed": closed,
                }

        # Create an embed to display the query dashboard
        embed = discord.Embed(title="Query Dashboard", color=theme)

        # Add fields for each query
        for query_id in query_ids:
            query = query_data[query_id]
            title = query["title"]
            category = query["category"]
            difficulty = query["difficulty"]
            closed = query["closed"]
            status = "Closed" if closed else "Open"
            # Create a formatted string to display the query information
            query_info = f"**Title:** {title}\n**Category:** {category}\n**Difficulty:** {difficulty}\n**Status:** {status}\n{divider}"

            # Add the query information as a field in the embed
            embed.add_field(name=query_id, value=query_info, inline=False)
        await ctx.followup.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Assist(bot))
