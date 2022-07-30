from io import BytesIO
from typing import List, Union
import disnake
from disnake.ext import commands
import os
from shutil import rmtree
import zipfile
import requests
import pathlib
from bot import CBCBot


class Download(commands.Cog):
    def __init__(self, bot: CBCBot) -> None:
        self.bot = bot
        self.path = str(pathlib.Path(__file__).parent.resolve())

    @commands.slash_command(name="download")
    async def download(self, inter: disnake.ApplicationCommandInteraction):
        pass

    @download.sub_command(name="info")
    async def info(self, inter: disnake.ApplicationCommandInteraction):
        await inter.response.send_message(
            embed=DownloadEmbed(self.bot.env.BOT_OWNER_AVATAR_URL)
        )

    @download.sub_command(name="release")
    async def release(
        self, inter: disnake.ApplicationCommandInteraction, game_version: str = "1.18.2"
    ):
        await inter.response.defer()
        file = self.cf_check_cache(game_version=game_version, rel_type=1)
        if file != None:
            await inter.edit_original_message(file=file)
        else:
            await inter.edit_original_message("Could not find a full release.")

    @download.sub_command(name="beta")
    async def beta(
        self, inter: disnake.ApplicationCommandInteraction, game_version: str = "1.18.2"
    ):
        await inter.response.defer()
        file = self.cf_check_cache(game_version=game_version, rel_type=2)
        if file != None:
            await inter.edit_original_message(file=file)
        else:
            await inter.edit_original_message("Could not find a beta release.")

    @download.sub_command(name="alpha")
    async def alpha(
        self, inter: disnake.ApplicationCommandInteraction, game_version: str = "1.18.2"
    ):
        await inter.response.defer()
        file = self.cf_check_cache(game_version=game_version, rel_type=3)
        if file != None:
            await inter.edit_original_message(file=file)
        else:
            await inter.edit_original_message("Could not find an alpha release.")

    @download.sub_command(name="nightly")
    async def nightly(self, inter: disnake.ApplicationCommandInteraction):
        auth = (self.bot.env.GH_API_USER, self.bot.env.GH_API_TOKEN)
        response = requests.get(
            url=self.bot.env.GH_API_URL + "/actions/artifacts",
            params={"per_page": 1},
            auth=auth,
        ).json()
        os.makedirs(self.path + "/cache/nightly/", exist_ok=True)
        if not str(response["artifacts"][0]["workflow_run"]["id"]) in os.listdir(
            path=self.path + "/cache/nightly/"
        ):
            await inter.response.defer()
            rmtree(self.path + "/cache/nightly/")

            with zipfile.ZipFile(
                file=BytesIO(
                    requests.get(
                        url=response["artifacts"][0]["archive_download_url"],
                        auth=auth,
                    ).content
                )
            ) as z:
                z.extract(
                    member=z.filelist[0],
                    path=self.path
                    + "/cache/nightly/"
                    + str(response["artifacts"][0]["workflow_run"]["id"]),
                )

        file = disnake.File(
            fp=self.path
            + "/cache/nightly/"
            + str(response["artifacts"][0]["workflow_run"]["id"])
            + "/"
            + os.listdir(
                path=self.path
                + "/cache/nightly/"
                + str(response["artifacts"][0]["workflow_run"]["id"])
            )[0]
        )

        if inter.response.is_done():
            await inter.edit_original_message(file=file)
        else:
            await inter.response.send_message(file=file)

    def cf_check_cache(self, game_version: str, rel_type: int):
        uri = "https://api.curseforge.com"
        headers = {"Accept": "application/json", "x-api-key": self.bot.env.CF_API_KEY}
        page = 0
        for i in range(10):
            response: List[dict] = requests.get(
                f"{uri}/v1/mods/{self.bot.env.CF_API_MOD_ID}/files",
                params={"gameVersion": game_version, "page": page},
                headers=headers,
            ).json()
            files = response["data"]
            for file in files:
                if (
                    file["releaseType"] in range(1, rel_type + 1)
                    and file["isAvailable"]
                ):
                    match file["releaseType"]:
                        case 1:
                            cache_dir = f"{self.path}/cache/release/"
                        case 2:
                            cache_dir = f"{self.path}/cache/beta/"
                        case 3:
                            cache_dir = f"{self.path}/cache/alpha/"
                    os.makedirs(cache_dir, exist_ok=True)
                    if not str(file["id"]) in os.listdir(path=cache_dir):
                        rmtree(cache_dir, ignore_errors=True)
                        os.makedirs(name=cache_dir + str(file["id"]))
                        with open(
                            cache_dir + str(file["id"]) + "/" + file["fileName"],
                            mode="wb",
                        ) as f:
                            f.write(
                                requests.get(
                                    url=file["downloadUrl"], stream=True
                                ).content
                            )
                    return disnake.File(
                        fp=cache_dir + str(file["id"]) + "/" + file["fileName"]
                    )
            page += response["pagination"]["pageSize"]
            if (
                response["pagination"]["totalCount"] - response["pagination"]["index"]
                <= response["pagination"]["pageSize"]
            ):
                return None
        return None


class DownloadEmbed(disnake.Embed):
    def __init__(self, icon_url: str):
        super().__init__(title="Downloads:")
        self.add_field(
            name="Release:",
            value="use `/download release`\nreturns the latest CurseForge release",
            inline=False,
        )
        self.add_field(
            name="Beta:",
            value="use `/download beta`\nreturns the latest CurseForge beta (might also return a release if it's more recent)",
            inline=False,
        )
        self.add_field(
            name="Alpha:",
            value="use `/download alpha`\nreturns the latest CurseForge alpha (might also return a release or beta if it's more recent)",
            inline=False,
        )
        self.add_field(
            name="Nightly:",
            value="use `/download nightly`\n(returns an automatically compiled .jar from the latest github commit)\nor follow the steps in https://github.com/rbasamoyai/CreateBigCannons/blob/1.18.2/download_nightly.md",
            inline=False,
        )
        self.set_footer(text="made with ❤️ by Robotix#2605", icon_url=icon_url)


def setup(bot: commands.Bot):
    bot.add_cog(Download(bot))
