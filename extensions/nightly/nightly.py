import os
import disnake
from disnake.ext import commands
import requests
from bot import CBCBot
import zipfile
from io import BytesIO
from time import sleep, time


class Nightly(commands.Cog):
    def __init__(self, bot: CBCBot) -> None:
        self.bot = bot
        self.uri = "https://api.github.com"
        self.auth = (self.bot.env.GH_USER, self.bot.env.GH_TOKEN)

    @commands.slash_command(name="nightly")
    async def nightly(self, inter: disnake.ApplicationCommandInteraction):
        response = requests.get(
            url=self.uri + "/repos/rbasamoyai/CreateBigCannons/actions/artifacts",
            params={"per_page": 1},
            auth=self.auth,
        ).json()

        f: str = None

        for f in os.listdir(path=self.bot.path + "/extensions/nightly/cache/"):
            if not f.endswith(str(response["artifacts"][0]["workflow_run"]["id"])):
                await inter.response.defer()
                os.remove(os.path.join(self.bot.path + "/extensions/nightly/cache/", f))
                self.download_jar(response=response)
                break

        if f == "" or f == None:
            await inter.response.defer()
            self.download_jar(response=response)

        file = disnake.File(
            fp=self.bot.path
            + "/extensions/nightly/cache/"
            + str(response["artifacts"][0]["workflow_run"]["id"])
            + "/"
            + os.listdir(
                path=self.bot.path
                + "/extensions/nightly/cache/"
                + str(response["artifacts"][0]["workflow_run"]["id"])
            )[0]
        )

        if inter.response.is_done():
            await inter.edit_original_message(file=file)
        else:
            await inter.response.send_message(file=file)

    def download_jar(self, response: requests.Response):
        with zipfile.ZipFile(
            file=BytesIO(
                requests.get(
                    url=response["artifacts"][0]["archive_download_url"],
                    auth=self.auth,
                ).content
            )
        ) as z:
            z.extract(
                member=z.filelist[0],
                path=self.bot.path
                + "/extensions/nightly/cache/"
                + str(response["artifacts"][0]["workflow_run"]["id"]),
            )


def setup(bot: commands.Bot):
    bot.add_cog(Nightly(bot))
