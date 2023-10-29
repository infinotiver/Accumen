import discord
from typing import Union
import string
import random
import nltk
from nltk.corpus import stopwords
import datetime

nltk.download("stopwords")
nltk.download("punkt")
theme = 0x01EAFE
secondary_theme = 0x3E3AF5
tertiary_theme = 0x271C41

divider = "<:D4:1074952383605506089><:D4:1074952383605506089><:D4:1074952383605506089><:D4:1074952383605506089><:D4:1074952383605506089><:D3:1074952381667741786><:D3:1074952381667741786><:D3:1074952381667741786><:D3:1074952381667741786><:D3:1074952381667741786><:D5:1074952388500262922><:D5:1074952388500262922><:D5:1074952388500262922><:D5:1074952388500262922><:D5:1074952388500262922><:D4:1074952383605506089><:D4:1074952383605506089><:D4:1074952383605506089><:D4:1074952383605506089><:D4:1074952383605506089>"


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


def generate_query_id(title, description):
    # Define the characters to use in the ID
    chars = string.ascii_letters + string.digits

    # Extract a keyword from the title and description
    keyword = extract_keyword(title, description)

    # Generate a random 3-character string
    rand_str = "".join(random.choices(chars, k=3))

    # Get the current timestamp
    timestamp_str = str(int(datetime.datetime.now().timestamp()))

    # Combine the keyword, random string, and timestamp to create the ID
    query_id = f"{keyword}_{rand_str}_{timestamp_str}"

    return query_id


def dembed(
    title: str = None,
    description: Union[str] = None,
    thumbnail: str = None,
    picture: str = None,
    url: str = None,
    color: Union[int, discord.Color] = 0x3E3AF5,
    footer: Union[str] = None,
    image: str = None,
    preset: str = None,
) -> discord.Embed:
    embed = discord.Embed()
    author = "Accumen"
    if color != theme:
        if isinstance(color, str):
            color = int(color.replace("#", "0x"), base=16)
        embed.color = color
    else:
        embed.color = color
    if title:
        embed.title = title
    if description:
        description = f"{description}\n{divider}"
        embed.description = description
    if thumbnail:
        embed.set_thumbnail(url=thumbnail)
    if picture:
        embed.set_image(url=picture)
    if image:
        embed.set_image(url=image)
    if url:
        embed.url = url
    if footer:
        if isinstance(footer, str):
            embed.set_footer(text=footer)
    if preset:
        if preset == "beta":
            author += " ∙ Beta Feature"
    embed.set_author(name=author)
    return embed
