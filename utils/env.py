from dotenv import load_dotenv
from os import environ
from typing import Set
from ast import literal_eval


class Env:
    def __init__(self) -> None:
        try:
            load_dotenv()
        except Exception:
            pass
        self.BOT_DISCORD_TOKEN: str = environ["BOT_DISCORD_TOKEN"]
        self.BOT_OWNER_AVATAR_URL: str = environ["BOT_OWNER_AVATAR_URL"]
        self.BOT_DEVELOPERS: Set[int] = set(map(int, literal_eval(environ["BOT_DEVELOPERS"])))
        self.BOT_AUTO_RELOAD: bool = environ["BOT_AUTO_RELOAD"]
        self.BOT_AUTO_LOAD: Set[str] = literal_eval(environ["BOT_AUTO_LOAD"])
        self.BOT_TEST_GUILDS: Set[int] = set(map(int, literal_eval(environ["BOT_TEST_GUILDS"])))

        self.MOD_LATEST_MC_VERSION: str = environ["MOD_LATEST_MC_VERSION"]

        self.GH_API_URL: str = environ["GH_API_URL"]
        self.GH_API_USER: str = environ["GH_API_USER"]
        self.GH_API_TOKEN: str = environ["GH_API_TOKEN"]

        self.CF_API_MOD_ID: str = environ["CF_API_MOD_ID"]
        self.CF_API_KEY: str = environ["CF_API_KEY"]

        self.STARS_VOTE_CHANNEL_ID: int = int(environ["STARS_VOTE_CHANNEL_ID"])
        self.STARS_REPOST_CHANNEL_ID: int = int(environ["STARS_REPOST_CHANNEL_ID"])
        self.STARS_THRESHOLD: int = int(environ["STARS_THRESHOLD"])
        self.STARS_BYPASS: Set[int] = set(map(int, literal_eval(environ["STARS_BYPASS"])))
