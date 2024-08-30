import disnake
from disnake.ext import commands
from bot import CBCBot


class TankTussle(commands.Cog):
    def __init__(self, bot: CBCBot) -> None:
        self.bot = bot

    @commands.slash_command(name="tanktussle")
    async def tanktussle(self, inter: disnake.ApplicationCommandInteraction):
        inter.response.send_message(
            """**Important note regarding Tank Tussle modpack issues**
Create Big Cannons is not responsible for any issues arising from modified versions of the Tank Tussle modpack. Please use the specifically curated mods in the modpack. Any issues related to modified versions of Tank Tussle will be ignored."""
        )


def setup(bot: commands.Bot):
    bot.add_cog(TankTussle(bot))
