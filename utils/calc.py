import simpcalc
import discord
from math import pi, tau, e, sqrt
from utils.functions import dembed


class InteractiveView(discord.ui.View):
    def __init__(self):
        super().__init__()
        if simpcalc.Calculate is None:
            raise AttributeError("Calculate class is not defined in simpcalc module.")
        self.calc = simpcalc.Calculate()

    @discord.ui.button(style=discord.ButtonStyle.gray, label="1", row=0)
    async def one(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.expr += "1"
        embed = dembed(description=f"```\n{self.expr}\n```")
        await interaction.response.edit_message(embed=embed)

    @discord.ui.button(style=discord.ButtonStyle.gray, label="2", row=0)
    async def two(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.expr += "2"

        embed = dembed(description=f"```\n{self.expr}\n```")
        await interaction.response.edit_message(embed=embed)

    @discord.ui.button(style=discord.ButtonStyle.gray, label="3", row=0)
    async def three(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.expr += "3"
        embed = dembed(description=f"```\n{self.expr}\n```")
        await interaction.response.edit_message(embed=embed)

    @discord.ui.button(style=discord.ButtonStyle.green, label="+", row=0)
    async def plus(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.expr += "+"
        embed = dembed(description=f"```\n{self.expr}\n```")
        await interaction.response.edit_message(embed=embed)

    @discord.ui.button(style=discord.ButtonStyle.green, label="^", row=0)
    async def exponent(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        self.expr += "^"
        embed = dembed(description=f"```\n{self.expr}\n```")
        await interaction.response.edit_message(embed=embed)

    @discord.ui.button(style=discord.ButtonStyle.gray, label="4", row=1)
    async def last(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.expr += "4"
        embed = dembed(description=f"```\n{self.expr}\n```")
        await interaction.response.edit_message(embed=embed)

    @discord.ui.button(style=discord.ButtonStyle.gray, label="5", row=1)
    async def five(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.expr += "5"
        embed = dembed(description=f"```\n{self.expr}\n```")
        await interaction.response.edit_message(embed=embed)

    @discord.ui.button(style=discord.ButtonStyle.gray, label="6", row=1)
    async def six(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.expr += "6"
        embed = dembed(description=f"```\n{self.expr}\n```")
        await interaction.response.edit_message(embed=embed)

    @discord.ui.button(style=discord.ButtonStyle.green, label="÷", row=1)
    async def divide(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.expr += "/"
        embed = dembed(description=f"```\n{self.expr}\n```")
        await interaction.response.edit_message(embed=embed)

    @discord.ui.button(style=discord.ButtonStyle.green, label="%", row=1)
    async def pcent(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.expr += "%"
        embed = dembed(description=f"```\n{self.expr}\n```")
        await interaction.response.edit_message(embed=embed)

    @discord.ui.button(style=discord.ButtonStyle.gray, label="7", row=2)
    async def seven(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.expr += "7"
        embed = dembed(description=f"```\n{self.expr}\n```")
        await interaction.response.edit_message(embed=embed)

    @discord.ui.button(style=discord.ButtonStyle.gray, label="8", row=2)
    async def eight(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.expr += "8"
        embed = dembed(description=f"```\n{self.expr}\n```")
        await interaction.response.edit_message(embed=embed)

    @discord.ui.button(style=discord.ButtonStyle.gray, label="9", row=2)
    async def nine(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.expr += "9"
        embed = dembed(description=f"```\n{self.expr}\n```")
        await interaction.response.edit_message(embed=embed)

    @discord.ui.button(style=discord.ButtonStyle.green, label="×", row=2)
    async def multiply(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        self.expr += "*"
        embed = dembed(description=f"```\n{self.expr}\n```")
        await interaction.response.edit_message(embed=embed)

    @discord.ui.button(style=discord.ButtonStyle.green, label="π", row=2)
    async def pie(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.expr += "π"
        embed = dembed(description=f"```\n{self.expr}\n```")
        await interaction.response.edit_message(embed=embed)

    @discord.ui.button(style=discord.ButtonStyle.gray, label=".", row=3)
    async def dot(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.expr += "."
        embed = dembed(description=f"```\n{self.expr}\n```")
        await interaction.response.edit_message(embed=embed)

    @discord.ui.button(style=discord.ButtonStyle.gray, label="0", row=3)
    async def zero(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.expr += "0"
        embed = dembed(description=f"```\n{self.expr}\n```")
        await interaction.response.edit_message(embed=embed)

    @discord.ui.button(style=discord.ButtonStyle.gray, label="00", row=3)
    async def double_zero(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        self.expr += "00"
        embed = dembed(description=f"```\n{self.expr}\n```")
        await interaction.response.edit_message(embed=embed)

    @discord.ui.button(style=discord.ButtonStyle.green, label="√", row=3)
    async def square_root(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        self.expr += "sqrt("
        embed = dembed(description=f"```\n{self.expr}\n```")
        await interaction.response.edit_message(embed=embed)

    @discord.ui.button(style=discord.ButtonStyle.green, label="-", row=3)
    async def minus(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.expr += "-"
        embed = dembed(description=f"```\n{self.expr}\n```")
        await interaction.response.edit_message(embed=embed)

    @discord.ui.button(style=discord.ButtonStyle.green, label="(", row=4)
    async def left_bracket(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        self.expr += "("
        embed = dembed(description=f"```\n{self.expr}\n```")
        await interaction.response.edit_message(embed=embed)

    @discord.ui.button(style=discord.ButtonStyle.green, label=")", row=4)
    async def right_bracket(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        self.expr += ")"
        embed = dembed(description=f"```\n{self.expr}\n```")
        await interaction.response.edit_message(embed=embed)

    @discord.ui.button(style=discord.ButtonStyle.blurple, label="=", row=4)
    async def equal(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            self.expr = self.expr.replace("π", str(pi))
            self.expr = await self.calc.calculate(self.expr)
        except:  # if you are function only, change this to BadArgument
            return await interaction.response.send_message(
                "Um, looks like you provided a wrong expression...."
            )
        embed = dembed(description=f"```\n{self.expr}\n```")
        await interaction.response.edit_message(embed=embed)

    @discord.ui.button(style=discord.ButtonStyle.red, label="Clear", row=4)
    async def clear(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.expr = ""
        embed = dembed(description=f"```\n{self.expr}\n```")
        await interaction.response.edit_message(embed=embed)

    @discord.ui.button(style=discord.ButtonStyle.red, label="⌫", row=4)
    async def back(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.expr = self.expr[:-1]
        embed = dembed(description=f"```\n{self.expr}\n```")
        await interaction.response.edit_message(embed=embed)

