from datetime import timedelta
from typing import List

import discord
from discord.ext import commands

from cbcbot.bot import CBCBot


class Stars(commands.Cog):
    def __init__(self, bot: CBCBot) -> None:
        self.bot = bot
        self.reposted = set()
        self.first_run = True

    async def reaction_has_bypass(self, reaction: discord.Reaction) -> bool:
        async for user in reaction.users():
            if user.id in self.bot.settings.STARS_BYPASS:
                return True
        return False

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, event: discord.RawReactionActionEvent):
        if self.first_run:
            repost_channel = self.bot.get_channel(self.bot.settings.STARS_REPOST_CHANNEL_ID)
            if repost_channel is None:
                return
            async for message in repost_channel.history(limit=25):
                if len(message.embeds) > 0:
                    first_embed = message.embeds[0]
                    if first_embed.footer.text is not None:
                        self.reposted.add(int(first_embed.footer.text))
            self.first_run = False

        if event.emoji.name == "⭐" and (
            (
                event.channel_id in self.bot.settings.STARS_VOTE_CHANNEL_IDS
                or event.user_id in self.bot.settings.STARS_BYPASS
            )
            and event.message_id not in self.reposted
        ):
            channel = self.bot.get_channel(event.channel_id)
            if channel is None:
                return
            message = await channel.fetch_message(event.message_id)
            if message.author == self.bot.user:
                return

            reactions = message.reactions
            for reaction in reactions:
                if reaction.emoji == "⭐" and (
                    (
                        reaction.count >= self.bot.settings.STARS_THRESHOLD
                        and message.created_at
                        > discord.utils.utcnow() - timedelta(days=7)
                        and (message.embeds or message.attachments)
                    )
                    or await self.reaction_has_bypass(reaction)
                ):
                    repost_channel = self.bot.get_channel(
                        self.bot.settings.STARS_REPOST_CHANNEL_ID
                    )
                    if repost_channel is None:
                        return

                    first_embed = (
                        discord.Embed(
                            color=discord.Colour.gold(),
                            url=message.jump_url,
                        )
                        .set_author(
                            name=message.author.display_name,
                            icon_url=message.author.display_avatar.url,
                        )
                        .set_footer(text=event.message_id)
                        .add_field(
                            name="Original message",
                            value=f"[Jump to message]({message.jump_url})",
                            inline=False,
                        )
                    )

                    if message.content is not None and message.content != "":
                        first_embed.add_field(
                            name="Message",
                            value=message.content,
                        )

                    attachments = list(message.attachments)
                    if len(attachments) > 0:
                        for i, attachment in enumerate(attachments):
                            first_embed.add_field(
                                name=f"Attachment {i + 1}",
                                value=attachment.url,
                                inline=False,
                            )
                        for i, attachment in enumerate(attachments):
                            if (
                                attachment.content_type is not None
                                and attachment.content_type.startswith("image")
                            ):
                                first_embed.set_image(url=attachment.url)
                                attachments.pop(i)
                                break

                    embeds, other_attachments = await self.make_image_embeds(
                        attachments
                    )
                    embeds.insert(0, first_embed)

                    try:
                        await repost_channel.send(embeds=embeds)
                        if other_attachments is not None and other_attachments != []:
                            await repost_channel.send(files=other_attachments)
                    finally:
                        self.reposted.add(event.message_id)

    async def make_image_embeds(
        self,
        attachments: List[discord.Attachment],
    ):
        embeds = []
        other_attachments = []
        for attachment in attachments:
            if attachment.content_type is not None and attachment.content_type.startswith(
                "image"
            ):
                embeds.append(
                    discord.Embed(colour=discord.Colour.gold()).set_image(
                        url=attachment.url
                    )
                )
            else:
                other_attachments.append(await attachment.to_file())
        return embeds, other_attachments


async def setup(bot: CBCBot):
    await bot.add_cog(Stars(bot))
