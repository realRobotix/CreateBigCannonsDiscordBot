import disnake
from disnake.ext import commands


class Curseforge(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.uri = "https://www.curseforge.com/minecraft/mc-mods/create-big-cannons"

    @commands.slash_command(name="curseforge")
    async def curseforge(self, inter: disnake.ApplicationCommandInteraction):
        pass

    @curseforge.sub_command(name="description")
    async def description(self, inter: disnake.ApplicationCommandInteraction):
        await inter.response.send_message(self.uri)

    @curseforge.sub_command(name="files")
    async def files(self, inter: disnake.ApplicationCommandInteraction):
        await inter.response.send_message(self.uri + "/files")


def setup(bot: commands.Bot):
    bot.add_cog(Curseforge(bot))
