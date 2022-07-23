from dotenv import load_dotenv
import os


class Env:
    def __init__(self) -> None:
        try:
            load_dotenv()
        except Exception:
            pass
        self.BOT_DISCORD_TOKEN: str = os.environ["BOT_DISCORD_TOKEN"]
        self.BOT_DEVELOPERS: set = os.environ["BOT_DEVELOPERS"]
        self.BOT_AUTO_RELOAD: bool = os.environ["BOT_AUTO_RELOAD"]
        self.BOT_AUTO_LOAD: bool = os.environ["BOT_AUTO_LOAD"]
