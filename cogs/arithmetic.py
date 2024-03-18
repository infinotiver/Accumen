import discord
import json
from discord.ext import commands
import utils.calc as calc
from discord import app_commands
import requests
import os
import utils.functions as funcs
from utils.functions import dembed
from io import BytesIO
import math
from math import gcd  # Import gcd function from math module
import sympy
import utils.maths as maths_funcs

maths_functions = {"GCD/HCF": "hcf", "LCM": "lcm"}


def calculate_square_root(number):
    if number < 0:
        raise ValueError("Number cannot be negative")
    return math.sqrt(number)


def calculate_gcd(numbers):
    """
    Calculates the GCD of a list of numbers using the gcd function from the math module.
    """
    if len(numbers) == 0:
        raise ValueError("Please provide at least one number")
    result = numbers[0]
    for i in range(1, len(numbers)):
        result = gcd(result, numbers[i])
    return result


def calculate_lcm(numbers):
    """
    Calculates the LCM of a list of numbers using the GCD and the formula: LCM(a, b) = abs(a*b) / gcd(a,b).
    """
    if len(numbers) == 0:
        raise ValueError("Please provide at least one number")
    result = numbers[0]
    for i in range(1, len(numbers)):
        result = abs(result * numbers[i]) // gcd(result, numbers[i])
    return result


def prime_factorization(number):
    """
    Calculates the prime factorization of a number and returns a dictionary with the prime factors as keys
    and their corresponding exponents as values.
    """
    if number < 2:
        raise ValueError("Number must be greater than or equal to 2")
    factors = {}
    i = 2
    while i * i <= number:
        if number % i:
            i += 1
        else:
            number //= i
            factors[i] = factors.get(i, 0) + 1
    if number > 1:
        factors[number] = factors.get(number, 0) + 1
    return factors


class Numbers(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    group = app_commands.Group(
        name="maths",
        description="Mathematical operations and calculations",
    )
    facts = app_commands.Group(
        name="fun-maths",
        description="Interesting facts about numbers",
    )

    @group.command(name="wolfram", description="Query Wolfram Alpha")
    @app_commands.describe(query="The query string to send to Wolfram Alpha")
    async def wolf(self, ctx, query: str):
        wolfid = os.environ["wolf"]
        try:
            fp = requests.get(
                f"http://api.wolframalpha.com/v1/simple?appid={wolfid}&i={query}&layout=labelbar&width=1000&fontsize=19"
            )
            fp.raise_for_status()
        except requests.exceptions.HTTPError:
            await ctx.response.send_message(
                embed=dembed(
                    description="An error occurred while querying Wolfram Alpha."
                )
            )
            return
        file = discord.File(BytesIO(fp.content), filename="output.png")
        await ctx.response.send_message(
            file=file,
            embed=funcs.dembed(
                title="Wolfram Alpha",
                description=f"This result is taken from Wolfram Alpha\nQuery: `{query}`",
            ),
        )

    @group.command(
        name="calculate", description="Calculate using interactive calculator"
    )
    async def interactive_calc(self, ctx):
        view = calc.InteractiveView()
        await ctx.response.send_message("```\n```", view=view)

    @facts.command(
        name="number-fact", description="Tells about a fact regarding number given"
    )
    @app_commands.describe(number="The number to get a fact about")
    async def mathfact(self, ctx, number: int):
        if number < 0:
            await ctx.response.send_message(
                embed=dembed(description="Negative numbers are not allowed")
            )
            return
        url = f"https://numbersapi.p.rapidapi.com/{str(number)}/math"
        querystring = {"fragment": "false", "json": "true"}
        headers = {
            "X-RapidAPI-Key": os.environ["rapidapi"],
            "X-RapidAPI-Host": "numbersapi.p.rapidapi.com",
        }
        try:
            response = requests.get(url, headers=headers, params=querystring)
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            await ctx.response.send_message(
                embed=dembed(
                    description="An error occurred while fetching the number fact."
                )
            )
            return
        d = json.loads(response.content)
        await ctx.response.send_message(
            embed=dembed(title=d["number"], description=d["text"])
        )

    @facts.command(
        name="year-fact", description="Tells about a fact regarding the year given"
    )
    @app_commands.describe(year="The year to get a fact about")
    async def yearfact(self, ctx, year: int):
        url = f"https://numbersapi.p.rapidapi.com/{str(year)}/year"
        querystring = {"fragment": "false", "json": "true"}
        headers = {
            "X-RapidAPI-Key": os.environ["rapidapi"],
            "X-RapidAPI-Host": "numbersapi.p.rapidapi.com",
        }
        try:
            response = requests.get(url, headers=headers, params=querystring)
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            await ctx.response.send_message(
                embed=dembed(
                    description="An error occurred while fetching the year fact."
                )
            )
            return
        d = json.loads(response.content)
        date = d.get("date", "??")
        await ctx.response.send_message(
            embed=dembed(title=d["number"], description=d["text"], footer=date)
        )

    @facts.command(name="maths-trivia", description="Trivia about an integer")
    async def triviafact(self, ctx):
        url = "https://numbersapi.p.rapidapi.com/random/trivia"
        querystring = {
            "min": "1",
            "max": "20",
            "fragment": "false",
            "notfound": "floor",
            "json": "true",
        }
        headers = {
            "X-RapidAPI-Key": os.environ["rapidapi"],
            "X-RapidAPI-Host": "numbersapi.p.rapidapi.com",
        }
        try:
            response = requests.get(url, headers=headers, params=querystring)
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            await ctx.response.send_message(
                embed=dembed(
                    description="An error occurred while fetching the trivia fact."
                )
            )
            return
        d = json.loads(response.content)
        print(d)
        await ctx.response.send_message(
            embed=dembed(title=d["number"], description=d["text"])
        )

    @group.command(name="simple-functions", description="Many mathematical functions")
    @app_commands.choices(
        func=[
            app_commands.Choice(name=name, value=value)
            for name, value in maths_functions.items()
        ]
    )
    @app_commands.describe(func="The mathematical function to calculate")
    @app_commands.describe(
        numbers="The numbers to perform the calculation on (split with ' | ' if required)"
    )
    async def math_functions(self, ctx, func: app_commands.Choice[str], numbers: str):
        num_string = numbers.split(" | ")
        for a in num_string:
            new = int(a)
            for i in range(len(num_string)):
                if num_string[i] == a:
                    num_string[i] = new
        text = ""
        if func.value == "lcm":
            try:
                ans = calculate_lcm(num_string)
                text = f"LCM : {ans}"
            except ValueError as e:
                await ctx.response.send_message(embed=dembed(description=str(e)))
                return
        elif func.value == "hcf":
            try:
                ans = calculate_gcd(num_string)
                text = f"HCF/GCD : {ans}"
            except ValueError as e:
                await ctx.response.send_message(embed=dembed(description=str(e)))
                return
        await ctx.response.send_message(embed=dembed(description=text))

    @group.command(name="factorial", description="Factorial of a number")
    @app_commands.describe(number="The number to calculate the factorial for")
    async def prime_factors(self, ctx, number: int):
        if number < 0:
            await ctx.response.send_message(
                embed=dembed(description="Negative numbers are not allowed")
            )
            return
        if number == 0 or number == 1:
            await ctx.response.send_message(
                embed=dembed(description="0 or 1 not allowed")
            )
            return
        result = prime_factorization(number)
        factors_str = " • ".join(
            [
                f"{factor}^{exponent}" if exponent > 1 else str(factor)
                for factor, exponent in result.items()
            ]
        )
        expanded_factors_str = " X ".join(
            [
                str(factor)
                for factor, exponent in result.items()
                for _ in range(exponent)
            ]
        )

        text = f"### Prime Factorization of {number}\n## {factors_str}\nNon exponential form\n{expanded_factors_str}"
        await ctx.response.send_message(embed=dembed(description=text))

    @group.command(
        name="roman-numerals",
        description="Convert hindu-arabic numerals to roman numerals or vice-versa",
    )
    @app_commands.choices(
        mode=[
            app_commands.Choice(name="Roman to Hindu Arabic", value=0),
            app_commands.Choice(name="Hindu Arabic to Roman", value=1),
        ]
    )
    @app_commands.describe(mode="The conversion mode to use")
    @app_commands.describe(number="The number to convert")
    async def roman_factors(self, ctx, mode: app_commands.Choice[int], number: str):
        converter = maths_funcs.int_roman()
        if mode.value == 1:
            # H ==> R
            result = converter.int_to_Roman(num=int(number))

            text = f"### Hindu Arabic to Roman\n**Result** : {result}"
        else:
            result = converter.roman_to_int(str(number))
            text = f"### Roman to Hindu Arabic\n**Result** : {result}"
        embed = dembed(description=text)
        await ctx.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Numbers(bot))
