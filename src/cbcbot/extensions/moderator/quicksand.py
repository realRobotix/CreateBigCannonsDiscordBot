from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from datetime import datetime, timedelta
from difflib import SequenceMatcher
from typing import Deque, Dict, Iterable, List

import discord
from discord.ext import commands

from cbcbot.bot import CBCBot


@dataclass
class QuicksandSnapshot:
    message: discord.Message
    normalized: str
    created_at: datetime


@dataclass
class QuicksandMatch:
    snapshot: QuicksandSnapshot
    similarity: float


class QuicksandActionView(discord.ui.View):
    def __init__(
        self,
        quicksand: "Quicksand",
        guild_id: int,
        user_id: int,
        message_summary: str,
        allow_unmute: bool,
        allow_mute: bool,
        allow_ban: bool,
        allow_unban: bool,
    ) -> None:
        super().__init__(timeout=quicksand.settings.QUICKSAND_ACTION_TIMEOUT_SECONDS)
        self.quicksand = quicksand
        self.guild_id = guild_id
        self.user_id = user_id
        self.message_summary = message_summary
        if allow_unmute:
            self.add_item(_QuicksandUnmuteButton())
        if allow_mute:
            self.add_item(_QuicksandMuteButton())
        if allow_ban:
            self.add_item(_QuicksandBanButton())
        if allow_unban:
            self.add_item(_QuicksandUnbanButton())


class _QuicksandUnmuteButton(discord.ui.Button):
    def __init__(self) -> None:
        super().__init__(label="Unmute", style=discord.ButtonStyle.success)

    async def callback(self, interaction: discord.Interaction) -> None:
        view = self.view
        if not isinstance(view, QuicksandActionView):
            return
        await view.quicksand.handle_unmute(interaction, view.guild_id, view.user_id)


class _QuicksandMuteButton(discord.ui.Button):
    def __init__(self) -> None:
        super().__init__(label="Mute Again", style=discord.ButtonStyle.secondary)

    async def callback(self, interaction: discord.Interaction) -> None:
        view = self.view
        if not isinstance(view, QuicksandActionView):
            return
        await view.quicksand.handle_remute(interaction, view.guild_id, view.user_id)


class _QuicksandBanButton(discord.ui.Button):
    def __init__(self) -> None:
        super().__init__(label="Ban User", style=discord.ButtonStyle.danger)

    async def callback(self, interaction: discord.Interaction) -> None:
        view = self.view
        if not isinstance(view, QuicksandActionView):
            return
        await view.quicksand.handle_ban(
            interaction, view.guild_id, view.user_id, view.message_summary
        )


class _QuicksandUnbanButton(discord.ui.Button):
    def __init__(self) -> None:
        super().__init__(label="Unban", style=discord.ButtonStyle.secondary)

    async def callback(self, interaction: discord.Interaction) -> None:
        view = self.view
        if not isinstance(view, QuicksandActionView):
            return
        await view.quicksand.handle_unban(interaction, view.guild_id, view.user_id)


class Quicksand(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.settings = bot.settings
        self.message_history: Dict[int, Deque[QuicksandSnapshot]] = {}

    def _normalize_message(self, message: discord.Message) -> str:
        parts: List[str] = []
        content = message.clean_content.strip().lower()
        if content:
            parts.append(content)
        for attachment in message.attachments:
            parts.append(f"attachment:{attachment.filename} {attachment.title} {attachment.size} {attachment.content_type}")
        for embed in message.embeds:
            if embed.title:
                parts.append(embed.title.strip().lower())
            if embed.description:
                parts.append(embed.description.strip().lower())
            if embed.url:
                parts.append(embed.url.strip().lower())
        return " ".join(parts)

    def _similarity(self, left: str, right: str) -> float:
        if not left and not right:
            return 1.0
        return SequenceMatcher(None, left, right).ratio()

    def _trim_history(self, history: Deque[QuicksandSnapshot]) -> None:
        if not self.settings.QUICKSAND_ENABLED:
            history.clear()
            return
        cutoff = discord.utils.utcnow() - timedelta(
            seconds=self.settings.QUICKSAND_WINDOW_SECONDS
        )
        while history and history[0].created_at < cutoff:
            history.popleft()

    def _select_matches(
        self, history: Iterable[QuicksandSnapshot], current: QuicksandSnapshot
    ) -> List[QuicksandMatch]:
        matches_by_channel: Dict[int, QuicksandMatch] = {}
        for snapshot in history:
            similarity = (
                1.0
                if snapshot.message.id == current.message.id
                else self._similarity(current.normalized, snapshot.normalized)
            )
            if similarity < self.settings.QUICKSAND_SIMILARITY_THRESHOLD:
                continue
            channel_id = snapshot.message.channel.id
            existing = matches_by_channel.get(channel_id)
            if existing is None or similarity > existing.similarity:
                matches_by_channel[channel_id] = QuicksandMatch(snapshot, similarity)
        return list(matches_by_channel.values())

    def _match_summary(self, matches: List[QuicksandMatch]) -> str:
        lines: List[str] = []
        for match in matches:
            message = match.snapshot.message
            content = message.clean_content or "[no text]"
            snippet = content[:300] + ("..." if len(content) > 300 else "")
            lines.append(
                f"- {message.channel.mention} ({match.similarity * 100:.1f}%): {snippet}"
            )
            if message.attachments:
                urls = ", ".join(attachment.url for attachment in message.attachments)
                lines.append(f"  attachments: {urls}")
        summary = "\n".join(lines)
        if len(summary) > 1800:
            summary = summary[:1800] + "..."
        return summary

    def _build_message_embed(self, match: QuicksandMatch) -> discord.Embed:
        message = match.snapshot.message
        description = message.clean_content or "[no text]"
        embed = discord.Embed(description=description)
        embed.add_field(name="Channel", value=message.channel.mention, inline=True)
        embed.add_field(
            name="Match", value=f"{match.similarity * 100:.1f}%", inline=True
        )
        embed.add_field(name="Jump", value=f"[Open]({message.jump_url})", inline=True)
        if message.attachments:
            attachment_urls = [attachment.url for attachment in message.attachments]
            embed.add_field(
                name="Attachments",
                value="\n".join(attachment_urls[:5]),
                inline=False,
            )
            for attachment in message.attachments:
                if attachment.content_type and attachment.content_type.startswith("image/"):
                    embed.set_image(url=attachment.url)
                    break
        if message.embeds:
            embed_summaries = []
            for original in message.embeds:
                title = original.title or "[embed]"
                if original.url:
                    embed_summaries.append(f"{title} ({original.url})")
                else:
                    embed_summaries.append(title)
            embed.add_field(
                name="Embeds",
                value="\n".join(embed_summaries[:5]),
                inline=False,
            )
        embed.set_author(name=message.author, icon_url=message.author.display_avatar.url)
        embed.timestamp = message.created_at
        return embed

    async def _get_report_channel(self, guild: discord.Guild) -> discord.TextChannel | None:
        channel = guild.get_channel(self.settings.QUICKSAND_REPORT_CHANNEL_ID)
        if channel is None:
            try:
                channel = await guild.fetch_channel(
                    self.settings.QUICKSAND_REPORT_CHANNEL_ID
                )
            except discord.NotFound:
                return None
        if isinstance(channel, discord.TextChannel):
            return channel
        return None

    async def _send_trigger_report(
        self, guild: discord.Guild, member: discord.Member, matches: List[QuicksandMatch]
    ) -> None:
        if not self.settings.QUICKSAND_ENABLED:
            return
        report_channel = await self._get_report_channel(guild)
        if report_channel is None:
            return
        matches = sorted(matches, key=lambda match: match.similarity, reverse=True)
        summary = discord.Embed(title="Quicksand Trigger", color=discord.Color.orange())
        summary.add_field(
            name="User",
            value=member.mention,
            inline=False,
        )
        summary.add_field(
            name="Channels",
            value=str(len({match.snapshot.message.channel.id for match in matches})),
            inline=True,
        )
        summary.add_field(name="Matches", value=str(len(matches)), inline=True)
        summary.add_field(
            name="Window",
            value=self._format_window(matches),
            inline=True,
        )
        summary.set_thumbnail(url=member.display_avatar.url)

        # all_exact = all(match.similarity >= 1.0 for match in matches)
        message_embeds: List[discord.Embed] = []
        # if all_exact and matches:
        #     message_embeds.append(self._build_message_embed(matches[0]))
        # else:
        message_embeds.extend(self._build_message_embed(match) for match in matches)

        view = QuicksandActionView(
            quicksand=self,
            guild_id=guild.id,
            user_id=member.id,
            message_summary=self._match_summary(matches),
            allow_unmute=True,
            allow_mute=False,
            allow_ban=True,
            allow_unban=False,
        )
        await report_channel.send(embeds=[summary, *message_embeds], view=view)

    async def _send_action_report(
        self,
        guild: discord.Guild,
        moderator: discord.Member | discord.User,
        user: discord.User,
        action: str,
        view: discord.ui.View | None,
    ) -> None:
        report_channel = await self._get_report_channel(guild)
        if report_channel is None:
            return
        embed = discord.Embed(title="Quicksand Action", color=discord.Color.blurple())
        embed.add_field(name="Action", value=action, inline=False)
        embed.add_field(name="Moderator", value=moderator.mention, inline=False)
        embed.add_field(name="User", value=user.mention, inline=False)
        await report_channel.send(embed=embed, view=view)

    async def _mute_member(self, member: discord.Member) -> None:
        role = member.guild.get_role(self.settings.QUICKSAND_MUTED_ROLE_ID)
        if role is None:
            return
        if role in member.roles:
            return
        await member.add_roles(role, reason="Quicksand spam detection")

    async def _unmute_member(self, member: discord.Member) -> None:
        role = member.guild.get_role(self.settings.QUICKSAND_MUTED_ROLE_ID)
        if role is None:
            return
        if role not in member.roles:
            return
        await member.remove_roles(role, reason="Quicksand unmute")

    async def handle_unmute(
        self, interaction: discord.Interaction, guild_id: int, user_id: int
    ) -> None:
        if not interaction.user.guild_permissions.manage_roles:
            await interaction.response.send_message(
                "You do not have permission to unmute users.", ephemeral=True
            )
            return
        guild = self.bot.get_guild(guild_id)
        if guild is None:
            await interaction.response.send_message(
                "Guild is unavailable.", ephemeral=True
            )
            return
        member = guild.get_member(user_id)
        if member is None:
            await interaction.response.send_message(
                "User is not in this guild.", ephemeral=True
            )
            return
        await self._unmute_member(member)
        await interaction.response.send_message(
            f"Unmuted {member.display_name}.", ephemeral=True
        )
        view = QuicksandActionView(
            quicksand=self,
            guild_id=guild.id,
            user_id=user_id,
            message_summary="",
            allow_unmute=False,
            allow_mute=True,
            allow_ban=True,
            allow_unban=False,
        )
        await self._send_action_report(
            guild, interaction.user, member, "Unmuted user", view
        )

    async def handle_remute(
        self, interaction: discord.Interaction, guild_id: int, user_id: int
    ) -> None:
        if not interaction.user.guild_permissions.manage_roles:
            await interaction.response.send_message(
                "You do not have permission to mute users.", ephemeral=True
            )
            return
        guild = self.bot.get_guild(guild_id)
        if guild is None:
            await interaction.response.send_message(
                "Guild is unavailable.", ephemeral=True
            )
            return
        member = guild.get_member(user_id)
        if member is None:
            await interaction.response.send_message(
                "User is not in this guild.", ephemeral=True
            )
            return
        await self._mute_member(member)
        await interaction.response.send_message(
            f"Muted {member.display_name} again.", ephemeral=True
        )

        view = QuicksandActionView(
            quicksand=self,
            guild_id=guild.id,
            user_id=user_id,
            message_summary="",
            allow_unmute=True,
            allow_mute=False,
            allow_ban=True,
            allow_unban=False,
        )
        
        await self._send_action_report(
            guild, interaction.user, member, "Muted user again", view
        )

    async def handle_ban(
        self,
        interaction: discord.Interaction,
        guild_id: int,
        user_id: int,
        message_summary: str,
    ) -> None:
        if not interaction.user.guild_permissions.ban_members:
            await interaction.response.send_message(
                "You do not have permission to ban users.", ephemeral=True
            )
            return
        guild = self.bot.get_guild(guild_id)
        if guild is None:
            await interaction.response.send_message(
                "Guild is unavailable.", ephemeral=True
            )
            return
        member = guild.get_member(user_id)
        if member is None:
            await interaction.response.send_message(
                "User is not in this guild.", ephemeral=True
            )
            return
        ban_message = (
            "You were banned for spam detected by quicksand.\n\n"
            f"Messages:\n{message_summary}"
        )
        try:
            await member.send(ban_message)
        except discord.Forbidden:
            pass
        await member.ban(reason="Quicksand ban", delete_message_days=0)
        await interaction.response.send_message(
            f"Banned {member.display_name}.", ephemeral=True
        )
        view = QuicksandActionView(
            quicksand=self,
            guild_id=guild.id,
            user_id=user_id,
            message_summary="",
            allow_unmute=False,
            allow_mute=False,
            allow_ban=False,
            allow_unban=True,
        )
        await self._send_action_report(
            guild, interaction.user, member, "Banned user", view
        )

    async def handle_unban(
        self, interaction: discord.Interaction, guild_id: int, user_id: int
    ) -> None:
        if not interaction.user.guild_permissions.ban_members:
            await interaction.response.send_message(
                "You do not have permission to unban users.", ephemeral=True
            )
            return
        guild = self.bot.get_guild(guild_id)
        if guild is None:
            await interaction.response.send_message(
                "Guild is unavailable.", ephemeral=True
            )
            return
        user = await self.bot.fetch_user(user_id)
        await guild.unban(user, reason="Quicksand unban")
        await interaction.response.send_message(
            f"Unbanned {user.display_name}.", ephemeral=True
        )
        await self._send_action_report(
            guild, interaction.user, user, "Unbanned user", None
        )

    def _format_window(self, matches: List[QuicksandMatch]) -> str:
        if not matches:
            return "0s"
        timestamps = [match.snapshot.message.created_at for match in matches]
        start = min(timestamps)
        end = max(timestamps)
        seconds = max(0, int((end - start).total_seconds()))
        return f"{seconds}s"

    @commands.Cog.listener("on_message")
    async def quicksand_watch(self, message: discord.Message) -> None:
        if not self.settings.QUICKSAND_ENABLED:
            return
        if message.guild is None or message.author.bot:
            return
        if message.channel.id not in self.settings.QUICKSAND_WATCH_CHANNEL_IDS:
            return
        if message.author.id in self.settings.QUICKSAND_EXEMPT_USER_IDS:
            return
        if any(
            role.id in self.settings.QUICKSAND_EXEMPT_ROLE_IDS
            for role in message.author.roles
        ):
            return

        history = self.message_history.setdefault(message.author.id, deque())
        self._trim_history(history)

        normalized = self._normalize_message(message)
        snapshot = QuicksandSnapshot(
            message=message,
            normalized=normalized,
            created_at=discord.utils.utcnow(),
        )
        history.append(snapshot)

        matches = self._select_matches(history, snapshot)
        if len(matches) < self.settings.QUICKSAND_MIN_MATCHES:
            return

        await self._mute_member(message.author)
        for match in matches:
            try:
                await match.snapshot.message.delete()
            except discord.Forbidden:
                continue
            except discord.NotFound:
                continue
        await self._send_trigger_report(message.guild, message.author, matches)
        history.clear()


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Quicksand(bot))
