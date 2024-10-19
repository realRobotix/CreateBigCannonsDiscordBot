import disnake
from disnake.ext import commands
from bot import CBCBot


class Nuclear(commands.Cog):
    def __init__(self, bot: CBCBot) -> None:
        self.bot = bot

    @commands.slash_command(name="nuclear")
    async def nuclear(self, inter: disnake.ApplicationCommandInteraction):
        await inter.response.send_message(
            """# CBC: Nuclear

is a **Create Big Cannons** addon that adds simple yet devastating integration between Create Big Cannons and Alex's Caves.

**Download links**
CurseForge: https://www.curseforge.com/minecraft/mc-mods/cbc-nuclear
Modrinth: https://modrinth.com/mod/cbc-nuclear

Note: This addon is currently only available for Create Big Cannons 0.5.4. Stay tuned for support for newer versions of Create Big Cannons.

Developed by <@371393915728822272>."""
        , allowed_mentions=disnake.AllowedMentions.none())


def setup(bot: commands.Bot):
    bot.add_cog(Nuclear(bot))
