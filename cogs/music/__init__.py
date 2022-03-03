import discord
import asyncio
from cogs.music._core_music import CoreMusic
from discord.ext import commands
from discord.ext.commands import Bot
from discord import ApplicationContext
from app.utils.logger import Logger
from cogs.music.player import Player


class VoiceConnectionError(commands.CommandError):
    """Custom Exception class for connection errors."""

    pass


class InvalidVoiceChannel(VoiceConnectionError):
    """Exception for cases of invalid Voice Channels."""

    pass


class Music(CoreMusic):
    __slots__ = ["bot", "players", "logger"]

    def __init__(self, bot: Bot):
        self.logger = Logger.generate()
        super(Music, self).__init__(bot)
        self.players: Player = {}

    async def join(self, ctx: ApplicationContext):
        if not ctx.channel:
            return
        try:
            # noinspection PyProtectedMember
            channel = ctx.author.guild._voice_states[ctx.author.id].channel
        except AttributeError:
            await ctx.respond(
                content="'Voice channel 연결하지 못하였습니다.\n 유효한 'Voice channel'에 자신이 들어와 있는지 확인바랍니다."
            )
            raise InvalidVoiceChannel(message="'Voice channel'에 연결하지 못하였습니다.")
        vc = ctx.voice_client
        if vc:
            if vc.channel.id == channel.id:
                return
            try:
                await vc.move_to(channel)
            except asyncio.TimeoutError:
                await ctx.respond(
                    content=f"Moving to channel: <{str(channel)}> timed out"
                )
                raise VoiceConnectionError(
                    f"Moving to channel: <{str(channel)}> timed out"
                )
        else:
            try:
                await channel.connect()
            except asyncio.TimeoutError:
                await ctx.respond(
                    content=f"Connecting to channel: <{str(channel)}> timed out"
                )
                raise VoiceConnectionError(
                    message=f"Connecting to channel: <{str(channel)}> timed out"
                )
        return await ctx.respond(f"{ctx.author.name}님 정상적으로 보이스 채널에 연결되었습니다.")

    @commands.slash_command()
    async def connect(self, ctx: ApplicationContext):
        """Joins a voice channel."""
        await self.join(ctx)

    @commands.slash_command()
    async def play(self, ctx: ApplicationContext, *, search: str):
        await ctx.trigger_typing()
        vc = ctx.voice_client
        if not vc:
            await self.join(ctx)

        player = self.get_player(ctx)
        pkg_resources = await self.check(ctx, search)
        return await player.queue.put(pkg_resources)


def setup(bot: Bot):
    bot.add_cog(Music(bot))

