import logging
import os
import pathlib

import discord
from discord.ext import commands

from cbcbot.utils.exeptions import ExtensionLoadExeption
from cbcbot.utils.settings import get_settings


class CBCBot(commands.Bot):
    def __init__(self) -> None:
        self.path = str(pathlib.Path(__file__).parent.resolve())
        self.settings = get_settings()
        self.auto_load_modules = {
            self.normalize_extension_name(extension)
            for extension in self.settings.BOT_AUTO_LOAD
        }

        logging.basicConfig(level=logging.INFO)
        intents = discord.Intents.all()
        super().__init__(
            command_prefix="!",
            intents=intents,
            owner_ids=self.settings.BOT_DEVELOPERS,
        )

    async def setup_hook(self) -> None:
        await self.load_all_base_extensions()
        await self.load_auto_extensions()
        if self.settings.BOT_TEST_GUILDS:
            for guild_id in self.settings.BOT_TEST_GUILDS:
                guild = discord.Object(id=guild_id)
                self.tree.copy_global_to(guild=guild)
                try:
                    await self.tree.sync(guild=guild)
                except discord.Forbidden as error:
                    logging.warning(
                        "Skipping command sync for guild %s: %s", guild_id, error
                    )
        else:
            await self.tree.sync()

    @staticmethod
    def normalize_extension_name(extension: str) -> str:
        if extension.startswith("cbcbot.extensions."):
            return extension
        if extension.startswith("extensions."):
            return f"cbcbot.{extension}"
        return f"cbcbot.extensions.{extension}"

    def extension_from_file_path(self, file_path: str) -> str:
        relative_path = os.path.relpath(file_path[:-3], self.path)
        dotted_path = relative_path.replace(os.sep, ".")
        return f"cbcbot.{dotted_path}"

    async def load_all_base_extensions(self) -> None:
        for dirpath, _, filenames in os.walk(f"{self.path}/extensions/base"):
            for file_name in filenames:
                full_path = os.path.join(dirpath, file_name)
                if file_name.endswith(".py") and not file_name.startswith("_"):
                    extension = self.extension_from_file_path(full_path)
                    try:
                        await self.load_extension(extension)
                    except Exception as error:
                        raise ExtensionLoadExeption(
                            f"Failed to load {extension}\n{error}"
                        ) from error

    async def load_auto_extensions(self) -> None:
        for dirpath, _, filenames in os.walk(f"{self.path}/extensions"):
            for file_name in filenames:
                full_path = os.path.join(dirpath, file_name)
                if file_name.endswith(".py") and not file_name.startswith("_"):
                    extension = self.extension_from_file_path(full_path)
                    if (
                        extension.startswith("cbcbot.extensions.base")
                        or extension not in self.auto_load_modules
                    ):
                        continue
                    try:
                        await self.load_extension(extension)
                    except Exception as error:
                        raise ExtensionLoadExeption(
                            f"Failed to load {extension}\n{error}"
                        ) from error


def main() -> None:
    try:
        bot = CBCBot()
        print("starting")
        bot.run(bot.settings.BOT_DISCORD_TOKEN)
    except KeyboardInterrupt:
        print("shutting down")
