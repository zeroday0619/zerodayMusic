import random
import asyncio
import discord
import itertools
from typing import Iterator
from async_timeout import timeout
from app.extension import YTDLSource
from app.utils import Logger

from discord import ApplicationContext as Context
from discord import Guild
from discord.ext.commands import Bot
from discord import TextChannel


class SongQueue(asyncio.Queue):
    logger = Logger.generate()
    _queue: list[YTDLSource]

    @logger.catch(level="DEBUG")
    def __getitem__(self, item) -> list[YTDLSource] | YTDLSource:
        if isinstance(item, slice):
            return list(itertools.islice(self._queue, item.start, item.stop, item.step))
        else:
            return self._queue[item]

    @logger.catch(level="DEBUG")
    def __iter__(self) -> Iterator:
        return self._queue.__iter__()

    @logger.catch(level="DEBUG")
    def __len__(self) -> int:
        return self.qsize()

    def clear(self) -> None:
        self.logger.debug("_queue clear")
        self._queue.clear()

    def shuffle(self) -> None:
        self.logger.debug("_queue shuffle")
        random.shuffle(self._queue)

    def remove(self, index: int) -> None:
        self.logger.debug(f"delete {self._queue[index]}")
        del self._queue[index]


class Player:
    __slots__ = (
        "bot",
        "_guild",
        "_channel",
        "_cog",
        "queue",
        "next",
        "current",
        "np",
        "_volume",
        "logger",
    )

    def __init__(self, ctx: Context):
        self.logger = Logger.generate()
        self.bot: Bot = ctx.bot
        self._guild: Guild = ctx.guild
        self._channel: TextChannel = ctx.channel
        self._cog = ctx.cog

        self.queue: SongQueue[list] = SongQueue()
        self.next = asyncio.Event()
        self._volume = 0.5
        self.np = None
        self.current = None
        ctx.bot.loop.create_task(self.player_lock())

    @property
    def volume(self):
        return self._volume

    @property
    def is_playing(self):
        return self.np and self.current

    @staticmethod
    async def create_embed(source, duration, requester, current, thumbnail):
        embed = (
            discord.Embed(
                title="Now playing",
                description=f"```css\n{await source.get_title()}\n```",
                color=discord.Color.blurple(),
            )
                .add_field(name="Duration", value=duration)
                .add_field(name="Requested by", value=requester)
                .add_field(
                name="Uploader",
                value=f"[{await current.data.get_uploader()}]({await current.data.get_uploader_url()})",
            )
                .add_field(
                name="URL", value=f"[Click]({await current.data.get_video_url()})"
            )
                .set_thumbnail(url=thumbnail)
        )
        return embed

    async def player_lock(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            self.next.clear()

            try:
                async with timeout(300):
                    source = await self.queue.get()
            except asyncio.TimeoutError:
                if self in self._cog.players.values():
                    return ""
                return

            source.volume = self.volume
            self.current = source

            try:
                self._guild.voice_client.play(
                    source,
                    after=lambda _: self.bot.loop.call_soon_threadsafe(self.next.set),
                )
            except TypeError as error:
                self.logger.error(error)
                pass

            embed = await self.create_embed(
                source=source.data,
                duration=await self.current.data.get_duration(),
                requester=self.current.requester,
                current=self.current,
                thumbnail=await self.current.data.get_thumbnail()
            )
            self.np = await self._channel.send(embed=embed)
            await self.next.wait()

            try:
                await self.np.delete()
            except discord.HTTPException as err:
                self.logger.error(err)

    async def stop(self):
        self.queue.clear()
        if self.np:
            await self._guild.voice_client.disconnect()
            self.np = None

    def destroy(self, guild):
        # Disconnect and Cleanup
        return self.bot.loop.create_task(self._cog.cleanup(guild))

