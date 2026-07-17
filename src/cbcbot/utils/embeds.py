import datetime
import subprocess
from typing import Dict

import discord


class SubprocessEmbed(discord.Embed):
    def __init__(self, process: subprocess.CompletedProcess):
        if process.returncode == 0:
            colour = discord.Colour.green()
        else:
            colour = discord.Colour.red()

        super().__init__(colour=colour)
        value = process.stdout + process.stderr
        if value == "" or value is None:
            value = "None"
        self.add_field(name="Output:", value=value)


class SimpleEmbed(discord.Embed):
    def __init__(
        self,
        fields: Dict[str, str],
        colour: discord.Colour,
        title: str,
        url: str = None,
        description: str = None,
        timestamp: datetime.datetime = None,
    ):
        super().__init__(
            colour=colour,
            title=title,
            url=url,
            description=description,
            timestamp=timestamp,
        )
        for key in fields:
            if fields[key] != "" and fields[key] is not None:
                self.add_field(name=key, value=fields[key])
