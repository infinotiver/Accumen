import discord
from discord.ext import commands
import os
import motor.motor_asyncio
from discord import app_commands
import typing
from utils.functions import dembed

# Database connection (replace with your credentials)
mongo_url = os.environ["mongodb"]
cluster = motor.motor_asyncio.AsyncIOMotorClient(mongo_url)
db = cluster["accumen"]
resources_collection = db["resources"]


class Resource(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.reviewers = [900992402356043806]  # List of reviewer user IDs
        self.required_approvals = 1  # Number of approvals needed for posting

    group = app_commands.Group(
        name="resources",
        description="Academia only commands",
        guild_ids=[976878887004962917],
    )

    async def resource_name_autocompletion(
        self, interaction: discord.Interaction, current: str
    ) -> typing.List[app_commands.Choice[str]]:
        data = []
        queries_cursor = resources_collection.find({})
        async for (
            query
        ) in queries_cursor:  # Iterate over the cursor to construct the choices
            title_words = query["name"].split()
            title = query["name"]
            id = query["id"]
            for word in title_words:
                if current.lower() in map(str.lower, title_words):
                    data.append(
                        app_commands.Choice(name=f"{title} - {id}", value=query["id"])
                    )
                    break
        return data

    @group.command(name="submit")
    @app_commands.choices(
        resource_type=[
            app_commands.Choice(name="Class Notes", value="class_notes"),
            app_commands.Choice(name="Revision Sheets", value="revision_sheets"),
            app_commands.Choice(
                name="Old Periodic/Weekly Assessments", value="assessments"
            ),
            app_commands.Choice(
                name="Previous Year Final Exam Question Papers", value="question_paper"
            ),
            app_commands.Choice(name="Online Resources", value="online_resources"),
            app_commands.Choice(name="Others", value="others"),
        ]
    )
    async def submit(
        self,
        ctx,
        resource_type: app_commands.Choice[str],
        name: str,
        attachment: discord.Attachment = None,
        *,
        description: str,
    ):
        """Submits a resource for review and potential posting in the forum channel."""
        # Extract file (optional)

        attachment_url = attachment.url

        # Basic validation
        if len(name) < 5:
            await ctx.response.send_message(
                "**Resource name must be at least 5 characters long.**"
            )
            return
        if len(description) < 10:
            await ctx.response.send_message(
                "**Resource description must be at least 10 characters long.**"
            )
            return
        id = str(await resources_collection.count_documents({}) + 1)
        # Store resource details in database
        new_resource = {
            "id": id,
            "type": resource_type.value,
            "name": name,
            "description": description,
            "author": ctx.user.id,
            "submitted_by": ctx.user.mention,
            "url": attachment_url,
            "status": "Submitted",
            "reviewers": self.reviewers,
            "votes": {"approve": 0, "reject": 0},
        }
        resources_collection.insert_one(new_resource)

        # Send confirmation message
        await ctx.response.send_message(
            embed=dembed(
                description=f"Thank you, {ctx.user.mention}! Your resource '**{name}**' (ID : `{id}` ) has been submitted for review."
            )
        )

        # Notify reviewers (optional)
        for reviewer_id in self.reviewers:
            reviewer = self.bot.get_user(reviewer_id)
            if reviewer:
                await reviewer.send(
                    f"**A new resource '{name}'(ID : `{id}` ) needs review!**"
                )

    @group.command(name="review")
    @commands.has_permissions(manage_messages=True)
    @app_commands.choices(
        action=[
            app_commands.Choice(name="Approve 👍🏻", value="approve"),
            app_commands.Choice(name="Reject 👎🏻", value="reject"),
        ]
    )
    @app_commands.autocomplete(name=resource_name_autocompletion)
    async def review(self, ctx, name: str, action: app_commands.Choice[str]):
        """Reviews a submitted resource (approve/reject)."""
        # Check if resource exists and user has permissions
        resource = resources_collection.find_one({"id": name.value})
        if not resource or not ctx.user.guild_permissions.manage_messages:
            await ctx.response.send_message("**You cannot review resources.**")
            return

        action = action.value

        # Update resource status and votes
        resource["votes"][action.lower()] += 1
        resources_collection.update_one({"id": resource["id"]}, {"$set": resource})

        # Check for required approvals and post to forum
        if resource["votes"]["approve"] >= self.required_approvals:
            await self.post_to_forum(resource)
            resources_collection.delete_one({"id": resource["id"]})
        elif resource["votes"]["reject"] > 0:
            resources_collection.delete_one({"id": resource["id"]})

        # Notify author
        author = self.bot.get_user(resource["author"])
        if author:
            await author.send(
                f"**Your resource '{name}' has been {action.upper()}d!**\n(Current votes: Approve: {resource['votes']['approve']}, Reject: {resource['votes']['reject']})"
            )

        # Send confirmation message to reviewer
        await ctx.response.send_message(
            f"**Resource '{name}' has been voted {action.upper()}(e)d.**"
        )

    @group.command(name="search")
    async def search(self, ctx, query: str, page: int = 1):
        """Searches for submitted resources based on keywords or filters."""
        # Define search filters (can be extended for additional criteria)
        filters = {"$text": {"$search": query}}

        # Pagination logic (adjust page size as needed)
        page_size = 10
        skip = (page - 1) * page_size
        sort = {"id": -1}  # Sort by newest first

        # Search resources in database
        resource_cursor = (
            resources_collection.find(
                filters, projection={"score": {"$meta": "textScore"}}, sort=sort
            )
            .skip(skip)
            .limit(page_size)
        )
        resources = list(resource_cursor)

        # Check if any resources found
        if not resources:
            await ctx.response.send_message(
                f"**No resources found matching '{query}'.**"
            )
            return

        # Build embed message with search results
        embed = discord.Embed(title="Search Results")
        for i, resource in enumerate(resources, start=skip + 1):
            score = resource.get("score", 0)  # Extract search score (optional)
            embed.add_field(
                name=f"{i}. {resource['name']}",
                value=f"{resource['description'][:100]} ({score:.2f})",  # Truncate description and show search score (optional)
                inline=False,
            )

        # Add pagination buttons (if needed)
        total_resources = resources_collection.count_documents(filters)
        total_pages = (total_resources + page_size - 1) // page_size
        if total_pages > 1:
            buttons = [
                (
                    "◀️",
                    lambda _: self.search(ctx, query, page - 1) if page > 1 else None,
                ),
                (
                    "▶️",
                    lambda _: (
                        self.search(ctx, query, page + 1)
                        if page < total_pages
                        else None
                    ),
                ),
            ]
            for label, callback in buttons:
                embed.set_footer(text=f"Page {page} of {total_pages}")
                await ctx.response.send_message(
                    embed=embed,
                    view=discord.View(
                        children=[
                            discord.Button(
                                style=discord.ButtonStyle.gray,
                                label=label,
                                callback=callback,
                            )
                        ]
                    ),
                )
        else:
            await ctx.response.send_message(embed=embed)


# ... (other commands and functionality)


async def setup(bot):
    await bot.add_cog(Resource(bot))
