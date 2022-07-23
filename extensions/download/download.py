import disnake
from disnake.ext import commands


class Download(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.slash_command(name="download")
    async def download(self, inter: disnake.ApplicationCommandInteraction):
        await inter.response.send_message(
            "https://github.com/rbasamoyai/CreateBigCannons/blob/1.18.2/DOWNLOAD.md"
        )


def setup(bot: commands.Bot):
    bot.add_cog(Download(bot))
