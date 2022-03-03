from discord import Intents

from app import ZerodayMusic


app = ZerodayMusic(
    message=[
        "Ver. 4.0.0a",
        "문의: @zeroday0619#2080"
    ],
    command_prefix="+",
    intents=Intents(
        bans=False,
        emojis=False,
        guilds=True,
        members=True,
        messages=True,
        reactions=True,
        typing=True,
        presences=True,
        voice_states=True,
        invites=False,
        webhooks=False,
        integrations=True,
    )
)
app.load_extensions(["cogs.music"])
app.launch()
