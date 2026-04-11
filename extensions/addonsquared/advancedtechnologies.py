import disnake
from disnake.ext import commands
from bot import CBCBot


class AdvancedTechnologies(commands.Cog):
    def __init__(self, bot: CBCBot) -> None:
        self.bot = bot

    @commands.slash_command(name="cbcat")
    async def cbcat(self, inter: disnake.ApplicationCommandInteraction):
        await inter.response.send_message(
            """The latest release of Create Big Cannons is not fully supported by the latest release of **CBC: Advanced Technologies (CBC:AT)**. This has led to various issues, most notably Big Cartridges not firing and various CBC:AT items crashing the game.
You can fix this issue by **downgrading Create Big Cannons and Create to v5.9.1 and v6.0.6 respectively**, or by **removing CBC:AT from your modpack**.
This situation is expected to change in the future with a fix by CBC:AT. **This is NOT an issue with Create Big Cannons and will not be fixed on this server.**"""
        , allowed_mentions=disnake.AllowedMentions.none())


def setup(bot: commands.Bot):
    bot.add_cog(AdvancedTechnologies(bot))
