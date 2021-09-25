import os
import discord
import youtube_dl
from dotenv import load_dotenv
from discord.ext import commands, tasks

load_dotenv()
discordToken = os.getenv("---discordTokenHere---")

intents = discord.Intents().all()
client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix="~", intents=intents)