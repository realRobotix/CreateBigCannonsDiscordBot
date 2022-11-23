import disnake
from disnake.ext import commands
from bot import CBCBot
from base64 import b64decode, b64encode


class Stars(commands.Cog):
    def __init__(self, bot: CBCBot) -> None:
        self.bot = bot
        self.reposted = set()
        self.first_run = True

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, event: disnake.RawReactionActionEvent):
        if self.first_run:
            repost_channel = self.bot.get_channel(self.bot.env.STARS_REPOST_CHANNEL_ID)
            messages = await repost_channel.history(limit=10).flatten()
            for message in messages:
                if len(message.embeds) > 0:
                    embed = message.embeds[0]
                    if (
                        type(embed.footer.text) != disnake.embeds._EmptyEmbed
                        and embed.footer != None
                        and embed.footer.text != None
                    ):
                        self.reposted.add(int(embed.footer.text))
            self.first_run = False
        if (
            event.emoji.name == "⭐"
            and event.channel_id == self.bot.env.STARS_VOTE_CHANNEL_ID
            and event.message_id not in self.reposted
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
                        and (message.embeds != None or message.attachments != None)
                    )
                    or await reaction.users().find(lambda u: u.id in self.bot.env.STARS_BYPASS) != None
                ):
                    # repost the message within an embed to the repost channel
                    repost_channel = self.bot.get_channel(self.bot.env.STARS_REPOST_CHANNEL_ID)

                    embed = (
                        disnake.Embed(
                            color=disnake.Colour.gold(),
                            url=message.jump_url,
                        )
                        .set_author(name=message.author.display_name, icon_url=message.author.avatar.url)
                        .set_footer(text=message.id)
                        .add_field(
                            name="Original message",
                            value=f"[Jump to message]({message.jump_url})",
                            inline=False,
                        )
                    )
                    if message.content != None and message.content != "":
                        embed.add_field(
                            name="Message",
                            value=message.content,
                        )
                    if len(message.attachments) > 0:
                        for i, attachment in enumerate(message.attachments):
                            embed.add_field(name=f"Attachment {i + 1}", value=attachment.url, inline=False)
                        if message.attachments[0].content_type.startswith("image"):
                            embed.set_image(url=message.attachments[0].url)
                        else:
                            await repost_channel.send(embed=embed)
                            await repost_channel.send(
                                files=[await attachment.to_file() for attachment in message.attachments]
                            )
                            return
                    if len(message.attachments) > 1:
                        await repost_channel.send(embed=embed)
                        await repost_channel.send(
                            files=[await attachment.to_file() for attachment in message.attachments[1:]]
                        )
                        return
                    else:
                        await repost_channel.send(embed=embed)
                    self.reposted.add(message.id)


def setup(bot: CBCBot):
    bot.add_cog(Stars(bot))
