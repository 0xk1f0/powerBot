import os
import discord
import toml
import uuid
import asyncio
from discord.ext import commands
from discord import app_commands
from src.spotify import perform_archive
from src.reddit import perform_fetch, ready_image, check_sub, TIMESPANS
from src.helpers import is_valid_url, gifReact
from src.lists import TRIGGERLIST
from datetime import datetime

# Load the config.toml file
config = toml.load("config.toml")

# Extract discord parameters from the config file
DAILY_ID = config["discord"]["daily_channel"]
DAILY_COUNT = int(config["discord"]["daily_count"])
DAILY_SUB = config["discord"]["daily_sub"]

# Extract general stuff from the config file
REDDIT_TOP_USAGE = config["general"]["reddit_top_usage"]
SPOTIFY_ARCHIVE_USAGE = config["general"]["spotify_archive_usage"]
SHOOT_USAGE = config["general"]["shoot_usage"]
HUG_USAGE = config["general"]["hug_usage"]
ERR = config["general"]["err"]
VERSION = config["version"]["tag"]
VERSION_CODENAME = config["version"]["codename"]
STATUS = config["general"]["status"]

# bot intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Create a bot object
bot = commands.Bot(command_prefix="/", intents=intents)

# on bot ready
@bot.event
async def on_ready():
    # sync
    try:
        await bot.tree.sync()
    except Exception as e:
        print(e)
    # set presence
    await bot.change_presence(activity=discord.Game(STATUS))
    # set daily task
    bot.loop.create_task(daily_ticker())

async def daily_ticker():
    await bot.wait_until_ready()
    channel = await bot.fetch_channel(DAILY_ID)
    while not bot.is_closed():
        now = datetime.now()
        if now.hour == 12 and now.minute == 0:
            result = await perform_fetch(DAILY_SUB, DAILY_COUNT, "day")
            if result != False and len(result) != 0:
                await channel.send(f"Time for r/{DAILY_SUB} Daily Top {DAILY_COUNT}!")
                for image in result:
                    # ALWAYS SEND DAILY WITH SPOILER
                    final = await ready_image(image, True)
                    if final != False:
                        message = await channel.send(file=final)
                        await message.add_reaction("👍")
                        await message.add_reaction("🫳")
                        await message.add_reaction("👎")
                    else:
                        continue
            else:
                await channel.send(f"{ERR}")
        await asyncio.sleep(60)

@bot.event
async def on_message(message):
	for word in TRIGGERLIST:
		if str(message.content).lower() == word[0] and message.author != bot.user:
			await message.channel.send(word[1])
			return
	await bot.process_commands(message)

@bot.tree.command(name="archive", description=SPOTIFY_ARCHIVE_USAGE)
@app_commands.describe(url = "URL of playlist to archive")
@app_commands.describe(format = "One of: 'json', 'txt'")
@app_commands.describe(reference = "Included in the output file")
async def archive(ctx: discord.Interaction, url: str, format: str, reference: str):
    if is_valid_url(url) != True:
        await ctx.response.send_message(f'"{url}" does not seem to be a valid URL!')
    elif format not in ["json", "txt"]:
        await ctx.response.send_message(f'"{format}" is unknown or unsupported!')
    else:
        id = url.split("/")[-1]
        await ctx.response.send_message(f"Archiving that for you..")
        result = await perform_archive(id, format, reference)
        if result != False:
            with open(os.path.join(f"{os.getcwd()}/data", f"playlist.{format}"), 'rb') as f:
                playlist_file = discord.File(f, filename=f"playlist_{reference}_{uuid.uuid4()}.{format}")
                await ctx.channel.send(f"Archived for you as .{format}! ^w^", file=playlist_file)
        else:
            await ctx.channel.send(f"{ERR}")

@bot.tree.command(name="top", description=REDDIT_TOP_USAGE)
@app_commands.describe(subreddit = "Target Subreddit")
@app_commands.describe(timespan = "Timespan of Posts")
@app_commands.describe(count = "Image Count")
async def top(ctx: discord.Interaction, subreddit: str, timespan: str, count: int):
    if timespan not in TIMESPANS:
        await ctx.response.send_message(f"Invalid Timespan, try one of: 'all', 'day', 'hour', 'month', 'week', 'year'")
    elif count > 25:
        await ctx.response.send_message(f"Max Count is capped to 25 for now!")
    else:
        is_sub = await check_sub(subreddit)
        if is_sub == False:
            await ctx.response.send_message(f"-.- could not find that subreddit..")
        else:
            nsfw_flag = is_sub[1]
            await ctx.response.send_message(f"^^ subreddit found! Fetching..")
            result = await perform_fetch(subreddit, count, timespan)
            if result != False and len(result) != 0:
                await ctx.channel.send(f"Top {count}/{timespan} images from r/{subreddit}")
                for image in result:
                    final = await ready_image(image, nsfw_flag)
                    if final != False:
                        await ctx.channel.send(file=final)
                    else:
                        continue
            else:
                await ctx.channel.send(f"{ERR}")

@bot.command(name="hug",description=HUG_USAGE)
async def hug(ctx):
    if not ctx.message.mentions:
        await ctx.send(f"{ERR} try: {HUG_USAGE}")
    else:
        user = ctx.message.mentions[0]
        gif = gifReact("hug")
        await ctx.send(f"{user.mention} {gif}")

@bot.command(name="shoot",description=SHOOT_USAGE)
async def shoot(ctx, id=""):
    if str(id) == "me":
        await ctx.send(f"I wouldn't do that..")
    elif not ctx.message.mentions:
        await ctx.send(f"{ERR} try: {SHOOT_USAGE}")
    else:
        user = ctx.message.mentions[0]
        gif = gifReact("shoot")
        await ctx.send(f"{user.mention} {gif}")

@bot.command(name="version")
async def version(ctx):
    await ctx.send(f'```Current Version: "{VERSION}" - "{VERSION_CODENAME}"```')

@bot.command(name="source")
async def source(ctx):
    await ctx.send(f"*On GitHub at https://github.com/0xk1f0/powerBot :)*")
