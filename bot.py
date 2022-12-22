import disnake
from disnake.ext import commands
from dotenv import load_dotenv
import pathlib
import logging
import os
from utils import env
from utils.exeptions import ExtensionLoadExeption


class CBCBot(commands.Bot):
    def __init__(self):
        self.path = str(pathlib.Path(__file__).parent.resolve())
        self.env = env.Env()
        logging.basicConfig(level=logging.INFO)
        super().__init__(
            test_guilds=self.env.BOT_TEST_GUILDS,
            intents=disnake.Intents.all(),
            sync_commands=True,
            reload=self.env.BOT_AUTO_RELOAD,
            owner_ids=self.env.BOT_DEVELOPERS,
        )

        for (dirpath, dirname, filenames) in os.walk(f"{self.path}/extensions/base"):
            for file in filenames:
                fullPath = os.path.join(dirpath, file)
                if file.endswith(".py") and not file.startswith("_"):
                    extension = (
                        "extensions." + fullPath[:-3].replace("/", ".").replace("\\", ".").split("extensions.")[1]
                    )
                    try:
                        self.load_extension(extension)
                    except Exception as e:
                        raise ExtensionLoadExeption(f"Failed to load {extension}\n{e}")
        for (dirpath, dirname, filenames) in os.walk(f"{self.path}/extensions"):
            for file in filenames:
                fullPath = os.path.join(dirpath, file)
                if file.endswith(".py") and not file.startswith("_"):
                    extension = (
                        "extensions." + fullPath[:-3].replace("/", ".").replace("\\", ".").split("extensions.")[1]
                    )
                    if extension.startswith("extensions.base") or extension not in self.env.BOT_AUTO_LOAD:
                        continue
                    try:
                        self.load_extension(extension)
                    except Exception as e:
                        raise ExtensionLoadExeption(f"Failed to load {extension}\n{e}")
        print("starting")
        self.run(self.env.BOT_DISCORD_TOKEN)


if __name__ == "__main__":
    try:
        bot = CBCBot()
    except KeyboardInterrupt:
        print("shutting down")
