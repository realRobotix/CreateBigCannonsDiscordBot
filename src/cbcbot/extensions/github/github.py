import discord
from discord import app_commands
from discord.ext import commands


class GitHub(commands.Cog):
    github = app_commands.Group(name="github", description="GitHub links")

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.url = "https://github.com/Cannoneers-of-Create/CreateBigCannons"

    @github.command(name="code")
    async def code(self, interaction: discord.Interaction):
        await interaction.response.send_message(self.url)

    @github.command(name="issues")
    async def issues(self, interaction: discord.Interaction):
        await interaction.response.send_message(self.url + "/issues")

    @github.command(name="prs")
    async def prs(self, interaction: discord.Interaction):
        await interaction.response.send_message(self.url + "/pulls")

    @github.command(name="builds")
    async def builds(self, interaction: discord.Interaction):
        await interaction.response.send_message(self.url + "/actions/workflows/gradle.yml")


async def setup(bot: commands.Bot):
    await bot.add_cog(GitHub(bot))
