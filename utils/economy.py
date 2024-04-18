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


# coins = current money, gems = special
async def get_user_data(id: int):
    """
    Retrieves user data from the economy collection based on the provided user ID.

    Args:
        id (int): The ID of the user to retrieve data for.

    Returns:
        data: The user data as a dictionary, or None if no data is found.
    """
    data = await economy_collection.find_one({"id": id})
    if data is None:
        await open_account(id)
        data = await economy_collection.find_one({"id": id})
    return data


async def open_account(id: int):
    newuser = {"id": id, "coins": 100, "gems": 0}

    await economy_collection.insert_one(newuser)


async def update_coins(id: int, coins: int):
    """
    A function to update the number of coins for a given id in the economy collection.

    Parameters:
    - id (int): The unique identifier of the record.
    - coins (int): The new number of coins to set.

    Returns:
    This function does not return anything.
    """
    if id is not None:
        await economy_collection.update_one({"id": id}, {"$set": {"coins": coins}})


async def update_gems(id: int, gems: int):
    if id is not None:
        await economy_collection.update_one({"id": id}, {"$set": {"gems": gems}})


async def add_coins(id: int, coins: int):
    """
    A function to add coins to a user's account based on their ID and the amount of coins to add.

    Parameters:
        id (int): The user's ID.
        coins (int): The amount of coins to add.

    Returns:
        None
    """
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
