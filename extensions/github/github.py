import disnake
from disnake.ext import commands


class GitHub(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.url = "https://github.com/rbasamoyai/CreateBigCannons"

    @commands.slash_command(name="github")
    async def github(self, inter: disnake.ApplicationCommandInteraction):
        pass

    @github.sub_command(name="code")
    async def code(self, inter: disnake.ApplicationCommandInteraction):
        await inter.response.send_message(self.url)

    @github.sub_command(name="issues")
    async def issues(self, inter: disnake.ApplicationCommandInteraction):
        await inter.response.send_message(self.url + "/issues")

    @github.sub_command(name="prs")
    async def prs(self, inter: disnake.ApplicationCommandInteraction):
        await inter.response.send_message(self.url + "/pulls")

    @github.sub_command(name="builds")
    async def prs(self, inter: disnake.ApplicationCommandInteraction):
        await inter.response.send_message(self.url + "/actions/workflows/gradle.yml")


def setup(bot: commands.Bot):
    bot.add_cog(GitHub(bot))
