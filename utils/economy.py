import motor.motor_asyncio
import nest_asyncio
import os
from dotenv import load_dotenv

nest_asyncio.apply()
os.chdir("..")
load_dotenv()
nest_asyncio.apply()

mongo_url = os.environ["mongodb"]

cluster = motor.motor_asyncio.AsyncIOMotorClient(mongo_url)
economy_collection = cluster["accumen"]["economy"]


async def get_user_data(id: int):
    await economy_collection.find_one({"id": id})


async def open_account(id: int):
    newuser = {"id": id, "coins": 100, "gems": 0}
    # coins = current money, gems = special
    await economy_collection.insert_one(newuser)


async def update_coins(id: int, coins: int):
    if id is not None:
        await economy_collection.update_one({"id": id}, {"$set": {"coins": coins}})


async def update_gems(id: int, gems: int):
    if id is not None:
        await economy_collection.update_one({"id": id}, {"$set": {"gems": gems}})


async def add_coins(id: int, coins: int):
    user = await economy_collection.find_one({"id": id})
    if user:
        coin_balance = user["coins"]
        coin_balance = +coins
        await update_coins(id, coin_balance)


async def add_gems(id: int, gems: int):
    user = await economy_collection.find_one({"id": id})
    if user:
        coin_balance = user["gems"]
        coin_balance = +gems
        await update_gems(id, coin_balance)
