from typing import List
import disnake
from disnake.ext import commands
import re


class Moderator(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.slash_command(name="moderator")
    async def moderator(self, inter: disnake.ApplicationCommandInteraction):
        pass

    @moderator.sub_command(name="purge")
    @commands.has_permissions(manage_messages=True)
    async def delete(
        self,
        inter: disnake.ApplicationCommandInteraction,
        limit: int,
        member: disnake.Member = None,
        regex: str = None,
        channel: disnake.TextChannel = None,
        server: bool = False,
    ):

        if regex != None:
            pattern = re.compile(regex)

        def check(m: disnake.Message):
            result = True
            if member != None:
                result = result and m.author == member
            if regex != None:
                result = result and re.search(pattern, m.clean_content) != None
            return result

        await inter.response.defer(ephemeral=True)
        if server:
            deleted: List[disnake.Message] = []
            for channel in inter.guild.text_channels:
                deleted.extend(await channel.purge(limit=limit, check=check, bulk=True))
        elif channel != None:
            deleted = await channel.purge(limit=limit, check=check, bulk=True)
        else:
            deleted = await inter.channel.purge(limit=limit, check=check, bulk=True)
        await inter.edit_original_message(content=f"deleted {len(deleted)} messages")


def setup(bot: commands.Bot):
    bot.add_cog(Moderator(bot))
