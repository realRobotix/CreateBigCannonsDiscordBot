import discord
from discord import app_commands
from discord.ext import commands


class Curseforge(commands.Cog):
    curseforge = app_commands.Group(
        name="curseforge", description="CurseForge links"
    )

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.uri = "https://www.curseforge.com/minecraft/mc-mods/create-big-cannons"

    @curseforge.command(name="description")
    async def description(self, interaction: discord.Interaction):
        await interaction.response.send_message(self.uri)

    @curseforge.command(name="files")
    async def files(self, interaction: discord.Interaction):
        await interaction.response.send_message(self.uri + "/files")


async def setup(bot: commands.Bot):
    await bot.add_cog(Curseforge(bot))
