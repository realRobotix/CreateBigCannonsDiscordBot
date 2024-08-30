import disnake
from disnake.ext import commands
from bot import CBCBot


class CBCModernwarfare(commands.Cog):
    def __init__(self, bot: CBCBot) -> None:
        self.bot = bot

    @commands.slash_command(name="modernwarfare")
    async def modernwarfare(self, inter: disnake.ApplicationCommandInteraction):
        await inter.response.send_message(
            """# CBC: Modern Warfare

is a **Create Big Cannons** addon that greatly expands on the core gameplay of the base mod with new features inspired by contemporary warfare, such as medium cannons, rotary autocannons, new mounts, and so much more.

Server link: https://discord.gg/HmZ8eAayKm

Note: This addon is still in development.

Developed by <@497573066100965377>."""
        )


def setup(bot: commands.Bot):
    bot.add_cog(CBCModernwarfare(bot))
