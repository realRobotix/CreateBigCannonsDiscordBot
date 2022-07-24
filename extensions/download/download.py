import disnake
from disnake.ext import commands
import requests
from bot import CBCBot
import zipfile
from io import BytesIO


class Download(commands.Cog):
    def __init__(self, bot: CBCBot) -> None:
        self.bot = bot
        self.uri = "https://api.github.com"
        self.auth = (self.bot.env.GH_USER, self.bot.env.GH_TOKEN)

    @commands.slash_command(name="download")
    async def download(self, inter: disnake.ApplicationCommandInteraction):
        await inter.response.defer()
        response = requests.get(
            url=self.uri + "/repos/rbasamoyai/CreateBigCannons/actions/artifacts",
            params={"per_page": 1},
            auth=self.auth,
        ).json()
        with zipfile.ZipFile(
            file=BytesIO(
                requests.get(
                    url=response["artifacts"][0]["archive_download_url"], auth=self.auth
                ).content
            )
        ) as z:
            await inter.edit_original_message(
                file=disnake.File(
                    fp=BytesIO(z.read(name=z.filelist[0])),
                    filename=z.filelist[0].filename,
                )
            )


def setup(bot: commands.Bot):
    bot.add_cog(Download(bot))
