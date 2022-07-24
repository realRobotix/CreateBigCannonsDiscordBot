import disnake
from disnake.ext import commands


class Download(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.slash_command(name="download")
    async def download(self, inter: disnake.ApplicationCommandInteraction):
        await inter.response.send_message(embed=DownloadEmbed())


class DownloadEmbed(disnake.Embed):
    def __init__(self):
        super().__init__(title="Downloads:")
        self.add_field(
            name="Release:",
            value="https://www.curseforge.com/minecraft/mc-mods/create-big-cannons/files",
            inline=False,
        )
        self.add_field(
            name="Nightly:",
            value="use `/nightly` or follow the steps in\nhttps://github.com/rbasamoyai/CreateBigCannons/blob/1.18.2/download_nightly.md",
            inline=False,
        )


def setup(bot: commands.Bot):
    bot.add_cog(Download(bot))
