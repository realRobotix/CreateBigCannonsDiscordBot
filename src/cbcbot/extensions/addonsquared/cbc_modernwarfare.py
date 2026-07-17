import discord
from discord import app_commands
from discord.ext import commands

from cbcbot.bot import CBCBot


class CBCModernwarfare(commands.Cog):
    def __init__(self, bot: CBCBot) -> None:
        self.bot = bot

    @app_commands.command(name="modernwarfare")
    async def modernwarfare(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            """# CBC: Modern Warfare

is a **Create Big Cannons** addon that greatly expands on the core gameplay of the base mod with new features inspired by contemporary warfare, such as medium cannons, rotary autocannons, new mounts, and so much more.

Server link: https://discord.gg/HmZ8eAayKm

Note: This addon is still in development.

Developed by <@497573066100965377>.""",
            allowed_mentions=discord.AllowedMentions.none(),
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(CBCModernwarfare(bot))
