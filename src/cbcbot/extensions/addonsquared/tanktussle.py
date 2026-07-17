import discord
from discord import app_commands
from discord.ext import commands

from cbcbot.bot import CBCBot


class TankTussle(commands.Cog):
    def __init__(self, bot: CBCBot) -> None:
        self.bot = bot

    @app_commands.command(name="tanktussle")
    async def tanktussle(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            """**Important note regarding Tank Tussle modpack issues**
Create Big Cannons is not responsible for any issues arising from modified versions of the Tank Tussle modpack. Please use the specifically curated mods in the modpack. Any issues related to modified versions of Tank Tussle will be ignored.""",
            allowed_mentions=discord.AllowedMentions.none(),
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(TankTussle(bot))
