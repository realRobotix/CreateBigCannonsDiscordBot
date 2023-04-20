import disnake
from disnake.ext import commands
from bot import CBCBot
from typing import List
from datetime import timedelta


class Stars(commands.Cog):
    def __init__(self, bot: CBCBot) -> None:
        self.bot = bot
        self.reposted = set()
        self.first_run = True

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, event: disnake.RawReactionActionEvent):
        if self.first_run:
            repost_channel = self.bot.get_channel(self.bot.env.STARS_REPOST_CHANNEL_ID)
            messages = await repost_channel.history(limit=25).flatten()
            for message in messages:
                if len(message.embeds) > 0:
                    first_embed = message.embeds[0]
                    if first_embed.footer.text != None:
                        self.reposted.add(int(first_embed.footer.text))
            self.first_run = False
        if event.emoji.name == "⭐" and (
            (event.channel_id in self.bot.env.STARS_VOTE_CHANNEL_IDS and event.message_id not in self.reposted)
            or event.user_id in self.bot.env.STARS_BYPASS
        ):
            channel = self.bot.get_channel(event.channel_id)
            message = await channel.fetch_message(event.message_id)
            if message.author == self.bot.user:
                return
            reactions = message.reactions
            for reaction in reactions:
                if reaction.emoji == "⭐" and (
                    (
                        reaction.count >= self.bot.env.STARS_THRESHOLD
                        and message.created_at > disnake.utils.utcnow() - timedelta(days=7)
                        and (message.embeds != None or message.attachments != None)
                    )
                    or await reaction.users().find(lambda u: u.id in self.bot.env.STARS_BYPASS) != None
                ):
                    # repost the message within an embed to the repost channel
                    repost_channel = self.bot.get_channel(self.bot.env.STARS_REPOST_CHANNEL_ID)

                    first_embed = (
                        disnake.Embed(
                            color=disnake.Colour.gold(),
                            url=message.jump_url,
                        )
                        .set_author(name=message.author.display_name, icon_url=message.author.avatar.url)
                        .set_footer(text=event.message_id)
                        .add_field(
                            name="Original message",
                            value=f"[Jump to message]({message.jump_url})",
                            inline=False,
                        )
                    )

                    if message.content != None and message.content != "":
                        first_embed.add_field(
                            name="Message",
                            value=message.content,
                        )

                    if len(message.attachments) > 0:
                        for i, attachment in enumerate(message.attachments):
                            first_embed.add_field(name=f"Attachment {i + 1}", value=attachment.url, inline=False)
                        for i, attachment in enumerate(message.attachments):
                            if attachment.content_type != None and attachment.content_type.startswith("image"):
                                first_embed.set_image(url=message.attachments.pop(i).url)
                                break

                    embeds, other_attachments = await self.make_image_embeds(message.attachments)
                    embeds.insert(0, first_embed)

                    try:
                        await repost_channel.send(embeds=embeds)
                        if other_attachments != None and other_attachments != []:
                            await repost_channel.send(files=other_attachments)
                    finally:
                        self.reposted.add(event.message_id)

    async def make_image_embeds(
        self,
        attachments: List[disnake.Attachment],
    ):
        embeds = []
        other_attachments = []
        for attachment in attachments:
            if attachment.content_type != None and attachment.content_type.startswith("image"):
                embeds.append(disnake.Embed(colour=disnake.Colour.gold()).set_image(url=attachment.url))
            else:
                other_attachments.append(await attachment.to_file())
        return embeds, other_attachments


def setup(bot: CBCBot):
    bot.add_cog(Stars(bot))
