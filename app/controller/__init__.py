from abc import ABCMeta
from typing import Optional
from discord import Intents
from discord.errors import ExtensionError

from app.services import ZerodayCore


class ZerodayMusic(ZerodayCore, metaclass=ABCMeta):
    __slots__ = ["message", "intents"]

    def __init__(
            self,
            message: list[str],
            intents: Intents,
            discord_token: Optional[str] = None,
            *args,
            **kwargs
    ):
        self.intents = intents
        super().__init__(
            message, intents, discord_token, *args, **kwargs
        )

    def load_extensions(self, cogs: Optional[list[str]]):
        self.logger.info(f"initialization cogs...")
        for cog in cogs:
            if cog is None:
                pass
            try:
                self.load_extension(cog)
            except ExtensionError as ext_error:
                self.logger.error(f"cog module: {ext_error.name}, {ext_error.args}")
