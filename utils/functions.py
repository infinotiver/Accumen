import discord
import random
from typing import Union, List, Dict
import motor.motor_asyncio
import nest_asyncio
import os

nest_asyncio.apply()
mongo_url = os.environ.get("mongodb")
cluster = motor.motor_asyncio.AsyncIOMotorClient(mongo_url)
levelling = cluster["accumen"]["level"]
# nltk.download("stopwords")
# nltk.download("punkt")
theme = 0x01EAFE
secondary_theme = 0x3E3AF5
tertiary_theme = 0x271C41

warning = 0xFFD700  # Yellow for warnings
error = 0xFF0000  # Red for errors
success = 0x00FF00  # Green for success messages
mild_error = 0xFFA500  # Orange for mild errors
info = 0x808080  # Gray for informational messages

# Divider string
divider = "<:D4:1074952383605506089><:D4:1074952383605506089><:D4:1074952383605506089><:D4:1074952383605506089><:D4:1074952383605506089><:D3:1074952381667741786><:D3:1074952381667741786><:D3:1074952381667741786><:D3:1074952381667741786><:D3:1074952381667741786><:D5:1074952388500262922><:D5:1074952388500262922><:D5:1074952388500262922><:D5:1074952388500262922><:D5:1074952388500262922><:D4:1074952383605506089><:D4:1074952383605506089><:D4:1074952383605506089><:D4:1074952383605506089><:D4:1074952383605506089>"


def dembed(
    title: str = None,
    description: Union[str, List[Union[str, Dict[str, str]]], Dict[str, str]] = None,
    thumbnail: str = None,
    picture: str = None,
    url: str = None,
    preset: str = None,
    footer: str = "Accumen",
    color: str = theme,
) -> discord.Embed:
    embed = discord.Embed()
    if color:
        if isinstance(color, str):
            color = int(color.replace("#", "0x"), base=16)
        embed = discord.Embed(color=color)

    if title:
        embed.title = title

    # Process description based on its type
    if description:
        if isinstance(description, str):
            description = f"{description}\n{divider}"
            embed.description = description
        elif isinstance(description, list):
            description = "\n".join(str(line) for line in description)
            embed.description = f"{description}\n{divider}"
        elif isinstance(description, dict):
            for key, value in description.items():
                embed.add_field(name=key, value=value, inline=False)

    if thumbnail:
        embed.set_thumbnail(url=thumbnail)
    if picture:
        embed.set_image(url=picture)
    if url:
        embed.url = url
    if footer:
        embed.set_footer(text=footer)

    if preset:
        if preset == "beta":
            embed.set_author(name="Accumen ∙ Beta Feature")

    return embed


async def add_xp(user_id, xp_amount):
    stats = await levelling.find_one({"id": user_id})

    if stats is None:
        new_user = {"id": user_id, "xp": xp_amount}
        await levelling.insert_one(new_user)
    else:
        xp = stats["xp"] + xp_amount
        levelling.update_one({"id": user_id}, {"$set": {"xp": xp}})

        lvl = 0
        while True:
            if xp < ((50 * (lvl**2)) + (50 * (lvl))):
                break
            lvl += 1
        xp -= (50 * ((lvl - 1) ** 2)) + (50 * (lvl - 1))

        if xp == 0:
            return f"Well done <@{user_id}>! You leveled up to **level: {lvl}**"


language_dict = [
    {"name": "Arabic", "code": "ar", "longCode": "ar"},
    {"name": "Asturian", "code": "ast", "longCode": "ast-ES"},
    {"name": "Belarusian", "code": "be", "longCode": "be-BY"},
    {"name": "Breton", "code": "br", "longCode": "br-FR"},
    {"name": "Danish", "code": "da", "longCode": "da-DK"},
    {"name": "German", "code": "de", "longCode": "de"},
    {"name": "Greek", "code": "el", "longCode": "el-GR"},
    {"name": "English", "code": "en", "longCode": "en"},
    {"name": "English (US)", "code": "en", "longCode": "en-US"},
    {"name": "English (Australian)", "code": "en", "longCode": "en-AU"},
    {"name": "English (Canadian)", "code": "en", "longCode": "en-CA"},
    {"name": "Spanish", "code": "es", "longCode": "es"},
    {"name": "Persian", "code": "fa", "longCode": "fa"},
    {"name": "French", "code": "fr", "longCode": "fr"},
    {"name": "Irish", "code": "ga", "longCode": "ga-IE"},
    {"name": "Italian", "code": "it", "longCode": "it"},
    {"name": "Japanese", "code": "ja", "longCode": "ja-JP"},
    {"name": "Dutch", "code": "nl", "longCode": "nl"},
    {"name": "Portuguese", "code": "pt", "longCode": "pt"},
    {"name": "Russian", "code": "ru", "longCode": "ru-RU"},
    {"name": "Swedish", "code": "sv", "longCode": "sv"},
    {"name": "Tamil", "code": "ta", "longCode": "ta-IN"},
    {"name": "Ukrainian", "code": "uk", "longCode": "uk-UA"},
    {"name": "Chinese", "code": "zh", "longCode": "zh-CN"},
]
"""
def extract_keyword(title, description):
    # Combine the title and description into a single text string
    text = f"{title} {description}"

    # Tokenize the text into words and remove stop words
    stop_words = set(stopwords.words("english"))
    words = [
        word.lower()
        for word in nltk.word_tokenize(text)
        if word.lower() not in stop_words and word.isalpha()
    ]

    # Count the frequency of each word and get the most common word that is at least 5 characters long
    freq_dist = nltk.FreqDist(words)
    keyword = next(
        (word for word, freq in freq_dist.most_common() if len(word) >= 5), ""
    )

    return keyword
"""
