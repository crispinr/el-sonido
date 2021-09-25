import os
from unicodedata import name
from async_timeout import asyncio
import discord
import youtube_dl
from dotenv import load_dotenv
from discord.ext import commands, tasks

load_dotenv()
discordToken = os.getenv("---discordTokenHere---")

intents = discord.Intents().all()
client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix="~", intents=intents)

youtube_dl.utils.bug_reports_message = lambda: ""

ytdl_format_options = {
    "format": "bestaudio/best",
    "restrictfilenames": True,
    "noplaylist": True,
    "nocheckcertificate": True,
    "ignoreerrors": False,
    "logtostderr": False,
    "quiet": True,
    "no_warnings": True,
    "default_search": "auto",
    "source_address": "0.0.0."
}

ffmpeg_options = {
    "options": "-vn"
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get("title")
        self.url = ""
    
    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        if "entries" in data:
            data = data["enteries"][0]
        filename = data["title"] if stream else ytdl.prepare_filename(data)
        return filename

@bot.command(name="join", help="Commands the bot to join the voice channel")
async def join(ctx):
    if not ctx.message.author.voice:
        await ctx.send("{} is not connected to a voice channel!".format(ctx.message.author.name))
        return
    else:
        channel = ctx.message.author.voice.channel
    await channel.connect()

@bot.command(name="leave", help="Commands the bot to leave the voice channel")
async def leave(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_connected():
        await voice_client.disconnect()
    else:
        await ctx.sent("Bot is not connected to a voice channel!")

@bot.command(name="play", help="Command bot to play a song")
async def play(ctx, url):
    try:
        server = ctx.message.guild
        voice_channel = server.voice_client

        async with ctx.typing():
            filename = await YTDLSource.from_url(url, loop=bot.loop)
            voice_channel.play(discord.FFmpegPCMAudio(executable="ffmpeg.exe", source=filename))
        await ctx.send("**Now playing: ** {}".format(filename))
    except:
        await ctx.send("Bot connected to voice channel!")

@bot.command(name="pause", help="Commands bot to pause the song")
async def pause(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        await voice_client.pause()
    else:
        await ctx.send("Bot is not playing anything at the moment")

@bot.command(name="resume", help="Commands bot to resume the song")
async def resume(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.ispaused():
        await voice_client.resume()
    else:
        await ctx.send("Bot is not playing anything! Use play command...")
