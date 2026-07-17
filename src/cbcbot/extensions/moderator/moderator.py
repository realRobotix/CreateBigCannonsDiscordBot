import re
from typing import List

import discord
from discord import app_commands
from discord.ext import commands


class Moderator(commands.Cog):
    moderator = app_commands.Group(name="moderator", description="moderation tools")

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @moderator.command(name="purge")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def delete(
        self,
        interaction: discord.Interaction,
        limit: int,
        member: discord.Member = None,
        regex: str = None,
        channel: discord.TextChannel = None,
        server: bool = False,
    ):
        if regex is not None:
            pattern = re.compile(regex)

        def check(message: discord.Message):
            result = True
            if member is not None:
                result = result and message.author == member
            if regex is not None:
                result = result and re.search(pattern, message.clean_content) is not None
            return result

        await interaction.response.defer(ephemeral=True)
        if server:
            deleted: List[discord.Message] = []
            for guild_channel in interaction.guild.text_channels:
                if guild_channel.permissions_for(interaction.guild.me).manage_messages:
                    deleted.extend(
                        await guild_channel.purge(limit=limit, check=check, bulk=True)
                    )
        elif channel is not None:
            deleted = await channel.purge(limit=limit, check=check, bulk=True)
        else:
            deleted = await interaction.channel.purge(limit=limit, check=check, bulk=True)
        await interaction.edit_original_response(content=f"deleted {len(deleted)} messages")


async def setup(bot: commands.Bot):
    await bot.add_cog(Moderator(bot))
