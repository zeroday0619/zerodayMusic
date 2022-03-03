import asyncio
import os
import discord
from abc import ABCMeta
from typing import Optional
from itertools import cycle
from discord.ext import commands
from discord.ext import tasks
from discord import Intents
from app.utils.logger import Logger
from app.utils.env import getenv


class ZerodayCore(commands.Bot, metaclass=ABCMeta):
    __slots__ = ["message", "intents"]

    def __init__(self, message: list[str], intents: Intents, discord_token: Optional[str] = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = Logger.generate()
        self.message = cycle(message)
        self.intents = intents

        # Discord bot token
        self.discord_token = discord_token or getenv(
            "ZERODAY_MUSIC_DISCORD_TOKEN",
            environment_variable_mode=True
        )

    async def on_ready(self):
        self.logger.info(f"Logged in as {self.user}")
        await self.change_status.start()

    @tasks.loop(seconds=30)
    async def change_status(self):
        msg = self.message
        await self.change_presence(
            status=discord.Status.streaming,
            activity=discord.Activity(
                name=next(msg),
                type=discord.ActivityType.playing
            ),
        )

    def launch(self) -> None:
        self.run(token=self.discord_token)
