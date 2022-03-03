import discord
from typing import Optional
from hqme.ext.platform import YouTube

FFMPEG_OPTIONS = {
    "before_options": "-reconnect 1 -reconnect_at_eof 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn",
}


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, requester, volume=0.5):
        super(YTDLSource, self).__init__(source, volume)
        self.requester = requester
        self.data: Optional[YouTube] = data

    def __getitem__(self, item):
        return self.__getattribute__(item)

    @classmethod
    async def auto_search(cls, ctx, url):
        soc = YouTube(url)
        await soc.sync()
        url = await soc.get_video_url()
        return cls(discord.FFmpegPCMAudio(url, **FFMPEG_OPTIONS), data=soc, requester=ctx.author)
