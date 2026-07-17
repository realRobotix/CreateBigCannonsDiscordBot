import os
import subprocess

import discord
from discord import app_commands
from discord.ext import commands

from cbcbot.bot import CBCBot
from cbcbot.utils.embeds import SubprocessEmbed


async def is_owner(interaction: discord.Interaction) -> bool:
    return await interaction.client.is_owner(interaction.user)


class Manager(commands.Cog):
    manager = app_commands.Group(
        name="manager", description="used to manage extensions"
    )
    extension = app_commands.Group(
        name="extension",
        description="extension management commands",
        parent=manager,
    )
    service = app_commands.Group(
        name="service",
        description="service management commands",
        parent=manager,
    )
    git = app_commands.Group(
        name="git",
        description="git commands",
        parent=manager,
    )

    def __init__(self, bot: CBCBot) -> None:
        self.bot = bot

    @extension.command(
        name="load", description='load an extension. use "all" to load all extensions'
    )
    @app_commands.check(is_owner)
    async def load(
        self, interaction: discord.Interaction, extension: str
    ) -> None:
        successful_loads = ""
        failed_loads = ""
        if extension == "all":
            for dirpath, _, filenames in os.walk(f"{self.bot.path}/extensions"):
                for file_name in filenames:
                    full_path = os.path.join(dirpath, file_name)
                    if file_name.endswith(".py") and not file_name.startswith("_"):
                        extension = (
                            "cbcbot."
                            + os.path.relpath(full_path[:-3], self.bot.path)
                            .replace(os.sep, ".")
                        )
                        if extension.startswith("cbcbot.extensions.base"):
                            continue
                        try:
                            await self.bot.load_extension(extension)
                            successful_loads += f"\nsuccessfully loaded {extension}"
                        except Exception as error:
                            failed_loads += f"\nfailed to load {extension}\n{error}"
        else:
            normalized_extension = self.bot.normalize_extension_name(extension)
            try:
                await self.bot.load_extension(normalized_extension)
                successful_loads += f"\nsuccessfully loaded {normalized_extension}"
            except Exception as error:
                failed_loads += f"\nfailed to load {normalized_extension}\n{error}"

        embed = self.create_embed(
            successful=successful_loads, failed=failed_loads, type="load"
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @extension.command(
        name="unload",
        description='unload an extension. use "all" to unload all extensions',
    )
    @app_commands.check(is_owner)
    async def unload(
        self, interaction: discord.Interaction, extension: str
    ) -> None:
        successful_unloads = ""
        failed_unloads = ""
        if extension == "all":
            for loaded_extension in list(self.bot.extensions):
                if loaded_extension.startswith("cbcbot.extensions.base"):
                    continue
                try:
                    await self.bot.unload_extension(loaded_extension)
                    successful_unloads += f"\nsuccessfully unloaded {loaded_extension}"
                except Exception as error:
                    failed_unloads += f"\nfailed to unload {loaded_extension}\n{error}"
        else:
            normalized_extension = self.bot.normalize_extension_name(extension)
            try:
                await self.bot.unload_extension(normalized_extension)
                successful_unloads += f"\nsuccessfully unloaded {normalized_extension}"
            except Exception as error:
                failed_unloads += f"\nfailed to unload {normalized_extension}\n{error}"
        embed = self.create_embed(
            successful=successful_unloads, failed=failed_unloads, type="unload"
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @extension.command(
        name="reload",
        description='reload an extension. use "all" to reload all extensions',
    )
    @app_commands.check(is_owner)
    async def reload(
        self, interaction: discord.Interaction, extension: str
    ) -> None:
        successful_reloads = ""
        failed_reloads = ""
        if extension == "all":
            for loaded_extension in list(self.bot.extensions):
                if loaded_extension.startswith("cbcbot.extensions.base"):
                    continue
                try:
                    await self.bot.reload_extension(loaded_extension)
                    successful_reloads += f"\nsuccessfully reloaded {loaded_extension}"
                except Exception as error:
                    failed_reloads += f"\nfailed to reload {loaded_extension}\n{error}"
        else:
            normalized_extension = self.bot.normalize_extension_name(extension)
            try:
                await self.bot.reload_extension(normalized_extension)
                successful_reloads += f"\nsuccessfully reloaded {normalized_extension}"
            except Exception as error:
                failed_reloads += f"\nfailed to reload {normalized_extension}\n{error}"

        embed = self.create_embed(
            successful=successful_reloads, failed=failed_reloads, type="reload"
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @extension.command(name="list", description="list all currently running extensions")
    @app_commands.check(is_owner)
    async def list(self, interaction: discord.Interaction) -> None:
        response = ""
        for key in self.bot.extensions.keys():
            response += key + "\n"
        await interaction.response.send_message(response, ephemeral=True)

    def create_embed(self, type: str, successful: str, failed: str) -> discord.Embed:
        successful = successful.strip()
        failed = failed.strip()
        colour = discord.Colour.orange()
        if successful == "" or successful is None:
            successful = "none"
            colour = discord.Colour.red()
        if failed == "" or failed is None:
            failed = "none"
            colour = discord.Colour.green()
        if successful != "none" and failed != "none":
            colour = discord.Colour.orange()
        embed = discord.Embed(title=f"Extensions {type}ed!", colour=colour)
        embed.add_field(
            name=f"Successful {type}s:", value=f"```{successful}```", inline=False
        )
        embed.add_field(name=f"Failed {type}s:", value=f"```{failed}```", inline=False)
        return embed

    @service.command(name="restart")
    @app_commands.check(is_owner)
    async def restart(self, interaction: discord.Interaction):
        process = subprocess.run(
            ["systemctl", "restart", "cbcbot"],
            cwd=self.bot.path,
            capture_output=True,
            encoding="utf-8",
        )
        await interaction.response.send_message(
            embed=SubprocessEmbed(process), ephemeral=True
        )

    @git.command(name="pull")
    @app_commands.check(is_owner)
    async def pull(self, interaction: discord.Interaction):
        process = subprocess.run(
            ["git", "pull"],
            cwd=self.bot.path,
            capture_output=True,
            encoding="utf-8",
        )
        await interaction.response.send_message(
            embed=SubprocessEmbed(process), ephemeral=True
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(Manager(bot))
