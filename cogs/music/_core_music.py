import discord
import itertools

from app.utils.logger import Logger
from discord.ext.commands import Bot, NoPrivateMessage
from discord import ApplicationContext as Context
from discord.ext import commands
from discord import Guild
from app.extension.youtube import YTDLSource
from cogs.music.player import Player
from validator_collection import checkers
from cogs.music.player import SongQueue


class VoiceConnectionError(commands.CommandError):
    """Custom Exception class for connection errors."""


class InvalidVoiceChannel(VoiceConnectionError):
    """Exception for cases of invalid Voice Channels."""


class CoreMusic(commands.Cog):
    """뮤직 모듈"""

    __slots__ = ("bot", "players", "logger")

    def __init__(self, bot: Bot):
        self.logger = Logger.generate()
        self.bot = bot
        self.players: Player = {}
        self.cog_version = "4.0.0a"
        self.ver_string = "Ver"

    async def cleanup(self, guild: Guild):
        """
        :param guild: Represents a Discord guild.
        """
        try:
            await guild.voice_client.disconnect()
        except AttributeError as e:
            raise e

        try:
            for source in self.players[guild.id].queue._queue:
                source.cleanup()

            del self.players[guild.id]

        except KeyError as e:
            raise e

    @staticmethod
    async def __local_check(ctx: Context):
        if not ctx.guild:
            raise NoPrivateMessage
        return True

    @staticmethod
    async def __error(ctx: Context, error):
        if isinstance(error, NoPrivateMessage):
            try:
                return await ctx.respond("이 Command 는 DM 에서 사용할 수 없습니다")
            except discord.HTTPException as e:
                raise e

        elif isinstance(error, InvalidVoiceChannel):
            return await ctx.respond(
                "Voice Channel 연결중 Error 가 발생하였습니다\n 자신이 Voice Channel에 접속되어 있는 지 확인 바랍니다."
            )

        Logger.generate().error("Ignoring exception in command {}".format(ctx.command))
        Logger.generate().exception(error)
        return await ctx.respond("ERROR: Ignoring exception in command {}".format(ctx.command))

    def get_player(self, ctx: Context):
        try:
            player = self.players[ctx.guild.id]
        except KeyError:
            player = Player(ctx)
            self.players[ctx.guild.id] = player
        return player

    async def sleep(self, ctx: Context, source):
        return source

    async def check(self, ctx: Context, search):
        try:
            if checkers.is_url(search):
                source = await YTDLSource.auto_search(ctx, search)
                return source
            else:
                search_text = search
                serc = search_text.replace(":", "")
                source = await YTDLSource.auto_search(ctx, serc)
                return source
        except Exception as e:
            Logger.generate().error(e)
            pass

    async def pause_embed(self, ctx: Context):
        nx = discord.Embed(
            title="Music",
            description=f"```css\n{ctx.author} : 일시중지.\n```",
            color=discord.Color.blurple(),
        ).add_field(name=self.ver_string, value=self.cog_version)
        return nx

    async def resume_embed(self, ctx: Context):
        nx = discord.Embed(
            title="Music",
            description=f"```css\n**{ctx.author}** : 다시재생.\n```",
            color=discord.Color.blurple(),
        ).add_field(name=self.ver_string, value=self.cog_version)
        return nx

    async def volume_embed(self, ctx: Context, vol):
        ix = discord.Embed(
            title="Music",
            description=f"```{ctx.author}: Set the volume to {vol}%```",
            color=discord.Color.blurple(),
        ).add_field(name=self.ver_string, value=self.cog_version)
        return ix

    async def now_playing_embed(self, vc):
        ex = discord.Embed(
            title=f"Now Playing: ```{vc.source.title}```",
            description=f"requested by @{vc.source.requester}",
            color=discord.Color.blurple(),
        ).add_field(name=self.ver_string, value=self.cog_version)
        return ex

    async def queue_info_embed(self, player):
        upcoming = list(itertools.islice(player.queue._queue, 0, 50))
        fmt = "\n".join(f'```css\n{_["title"]}\n```' for _ in upcoming)
        embed_queue = discord.Embed(
            title=f"Upcoming - Next **{len(upcoming)}**",
            description=fmt,
            color=discord.Color.blurple(),
        ).add_field(name=self.ver_string, value=self.cog_version)
        return embed_queue