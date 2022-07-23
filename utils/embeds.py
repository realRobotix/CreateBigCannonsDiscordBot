import disnake
from disnake.ext import commands
import subprocess
from typing import *
import datetime


class SubprocessEmbed(disnake.Embed):
    def __init__(self, process: subprocess.CompletedProcess):
        if process.returncode == 0:
            colour = disnake.Colour.green()
        else:
            colour = disnake.Colour.red()
        super().__init__(colour=colour)
        value = process.stdout + process.stderr
        if value == "" or value == None:
            value = "None"
        self.add_field(name="Output:", value=value)


class SimpleEmbed(disnake.Embed):
    def __init__(
        self,
        fields: Dict[str, str],
        colour: disnake.Colour,
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
            if fields[key] != "" and fields[key] != None:
                self.add_field(name=key, value=fields[key])
