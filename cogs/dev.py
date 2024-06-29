from discord.ext import commands
from discord import app_commands
import motor.motor_asyncio
import nest_asyncio
import os

nest_asyncio.apply()
mongo_url = os.environ["mongodb"]
cluster = motor.motor_asyncio.AsyncIOMotorClient(mongo_url)
system_data = cluster["accumen"]["system"]


class Dev(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    group = app_commands.Group(name="dev", description="developer only commands")

    @commands.Cog.listener()
    async def on_interaction(self, interaction):
        if str(interaction.type) == "InteractionType.application_command":
            counts_entry = await system_data.find_one({"_id": "commands_usage"})
            if counts_entry is not None:
                counts = counts_entry["count"] + 1
                await system_data.update_one(
                    {"_id": "commands_usage"}, {"$set": {"count": counts}}
                )
                print(counts)
            else:
                await system_data.insert_one({"_id": "commands_usage", "count": 1})


async def setup(bot):
    await bot.add_cog(Dev(bot))
