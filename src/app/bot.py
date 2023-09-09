import os
import discord
import toml
import re
from aiohttp import ClientSession, TCPConnector
from discord.ext import commands, tasks
from discord import app_commands
from datetime import datetime
from app.integrations.reddit import perform_fetch, save_units, check_sub, TIMESPANS
from app.integrations.wfp import get_wfps, SFW_CATEGORIES, NSFW_CATEGORIES, TYPES
from app.integrations.macvendor import get_mac_vendor, checkMAC

# Load the config.toml file with blocklist
CFG_PATH = os.getenv('CONF_PATH') or '/var/lib/powerBot/config'
CONFIG = toml.load(os.path.join(CFG_PATH, 'config.toml'))
BLOCKLIST = os.getenv('CONF_PATH') or '/var/lib/powerBot/config'
BLOCKLIST = toml.load(os.path.join(BLOCKLIST, 'blocklist.toml'))
VERSION = toml.load("VERSION")

# data path for cache
DATA_PATH = os.getenv('CONF_PATH') or '/var/lib/powerBot/data'

# Extract discord parameters from the config file
DAILY_ID = CONFIG["discord"]["daily_channel"]
DAILY_COUNT = int(CONFIG["discord"]["daily_count"])
DAILY_SUB = CONFIG["discord"]["daily_sub"]

# Extract blocking stuff
BLOCKED_USERS = BLOCKLIST["blocked"]["users"]

# Extract general stuff from the config file
ADMINS = CONFIG["general"]["admins"]
TRIGGERLIST = CONFIG["triggers"]["list"]
REDDIT_CAP = CONFIG["reddit"]["fetch_cap"]
ERR = CONFIG["general"]["err"]
STATUS = CONFIG["general"]["status"]
TAG = VERSION["tag"]

# bot intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Create a bot object
bot = commands.Bot(command_prefix="/", intents=intents)

# client session
client_session = None

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
    # new aiohttp session
    global client_session
    client_session = ClientSession(
        connector=TCPConnector(
            limit=20
        )
    )
    # set daily task
    daily_ticker.start()

### TASKS ###

@tasks.loop(seconds=60)
async def daily_ticker():
    now = datetime.now()
    if now.hour == 12 and now.minute == 1:
        await bot.wait_until_ready()
        channel = await bot.fetch_channel(DAILY_ID)
        result = await perform_fetch(
            DAILY_SUB,
            DAILY_COUNT,
            "day",
            (".jpg",".jpeg",".png"),
            client_session
        )
        if result != False and len(result) != 0:
            await channel.send(f"Time for r/{DAILY_SUB} Daily Top {DAILY_COUNT}!")
            for image in result:
                # ALWAYS SEND DAILY WITH SPOILER
                final = await save_units(image[0], True, client_session)
                if final != False:
                    message = await channel.send(file=final)
                    await message.add_reaction("👍")
                    await message.add_reaction("🫳")
                    await message.add_reaction("👎")
                else:
                    continue
        else:
            await channel.send(f"{ERR}")

### EVENTS ###

@bot.event
async def on_message(message):
	for word in TRIGGERLIST:
		if word[0] in str(message.content).lower() and message.author != bot.user:
			await message.channel.send(word[1])
			return
	await bot.process_commands(message)

### MAIN ###

@bot.tree.command(name="top", description=CONFIG["general"]["reddit_top_usage"])
@app_commands.describe(subreddit = "Target Subreddit")
@app_commands.describe(timespan = f"Timespan: {TIMESPANS}")
@app_commands.describe(count = "Image Count")
async def top(ctx: discord.Interaction, subreddit: str, timespan: str, count: int):
    if ctx.user.id in BLOCKED_USERS:
        await ctx.response.send_message(f'You are currently on the blocklist!')
        return
    if timespan not in TIMESPANS:
        await ctx.response.send_message(f"Invalid Timespan, try one of: {TIMESPANS}")
    elif count > int(REDDIT_CAP):
        await ctx.response.send_message(f"Max Count is capped to {REDDIT_CAP}!")
    else:
        is_sub = await check_sub(subreddit, client_session)
        if is_sub == False:
            await ctx.response.send_message(f"-.- could not find that subreddit..")
        else:
            await ctx.response.defer()
            result = await perform_fetch(
                subreddit,
                count,
                timespan,
                (".jpg",".jpeg",".png", ".gif", ".mp4"),
                client_session
            )
            if result != False and len(result) != 0:
                await ctx.followup.send(f"Top {count}/{timespan} images from r/{subreddit}")
                for unit in result:
                    if unit[1] == True:
                        await ctx.channel.send(f"|| {unit[0]} ||")
                    else:
                        await ctx.channel.send(unit[0])
            else:
                await ctx.followup.send(f"{ERR}")

@bot.tree.command(name="wfp", description=CONFIG["general"]["wfp_usage"])
@app_commands.describe(type = f"Type: {TYPES}")
@app_commands.describe(category = f"Image Category: {SFW_CATEGORIES + NSFW_CATEGORIES}")
@app_commands.describe(count = "Image Count")
async def wft(ctx: discord.Interaction, type: str, category: str, count: int):
    # check if user is blocked
    if ctx.user.id in BLOCKED_USERS:
        await ctx.response.send_message(f'You are currently on the blocklist!')
        return
    # check selected type
    if type not in TYPES:
        await ctx.response.send_message(f"Invalid Type, try one of: {TYPES}")
        return
    # check category
    if type == "sfw":
        CHOOSEN_CATS = SFW_CATEGORIES
    else:
        CHOOSEN_CATS = NSFW_CATEGORIES
    if category not in CHOOSEN_CATS:
        await ctx.response.send_message(f"Invalid Type, try one of: {CHOOSEN_CATS}!")
    elif count > int(REDDIT_CAP):
        await ctx.response.send_message(f"Max Count is capped to {REDDIT_CAP}!")
    else:
        await ctx.response.defer()
        result = await get_wfps(type, category, count, client_session)
        if result != False or None and len(result) != 0:
            await ctx.followup.send(f"Here are {count} {type} {category}'s")
            for unit in result:
                if unit[1] == "nsfw":
                    await ctx.channel.send(f"|| {unit[0]} ||")
                else:
                    await ctx.channel.send(unit[0])
        else:
            await ctx.followup.send(f"{ERR}")

@bot.tree.command(name="mac", description=CONFIG["general"]["mac_usage"])
@app_commands.describe(mac = "A valid MAC Address")
async def wft(ctx: discord.Interaction, mac: str):
    # check if user is blocked
    if ctx.user.id in BLOCKED_USERS:
        await ctx.response.send_message(f'You are currently on the blocklist!')
        return
    # check validity else proceed
    if not checkMAC(mac):
        await ctx.response.send_message(f"That MAC just doesn't look right..")
        return
    else:
        await ctx.response.defer()
        result = await get_mac_vendor(mac, client_session)
        if result != False or None:
            await ctx.followup.send(f"MAC belongs to: {result}")
        else:
            await ctx.followup.send(f"{ERR}")

### MODERATION ###

@bot.tree.command(name="purge", description="Delete the next x Messages")
@app_commands.describe(message_id = "ID of the Message above Start")
@app_commands.describe(count = "Number of Messages to Purge")
async def purge_reply(ctx: discord.Interaction, message_id: str, count: int):
    # check if user is blocked
    if ctx.user.id in BLOCKED_USERS:
        await ctx.response.send_message(f'You are currently on the blocklist!')
        return
    # check if user is admin
    if not ctx.user.id in ADMINS:
        await ctx.response.send_message(f'You are not an admin!')
        return
    try:
        # fetch message by ID
        MESSAGE = await ctx.channel.fetch_message(message_id)
        # get the history after message id
        HISTORY = [message async for message in ctx.channel.history(after=MESSAGE, limit=count)]
        # delete it
        if HISTORY and len(HISTORY) > 0:
            await ctx.response.defer()
            await ctx.channel.delete_messages(HISTORY)
        else:
            await ctx.response.send_message('No Messages to delete!')
    except:
        await ctx.followup.send(f"{ERR}")
    finally:
        await ctx.followup.send(f'Deleted {len(HISTORY)} message/s!')

### BLOCKING ###

@bot.tree.command(name="block", description="Block a user")
@app_commands.describe(user = "Target User")
async def block(ctx: discord.Interaction, user: str):
    global BLOCKLIST
    global BLOCKED_USERS

    # check if user is admin
    if not ctx.user.id in ADMINS:
        await ctx.response.send_message(f'You are not an admin!')
    else:
        # convert to normal id
        user_id = int(re.search(r'\d+', user).group())

        # check if user is not blocked already -> block
        if not user_id in BLOCKLIST["blocked"]["users"]:
            BLOCKLIST["blocked"]["users"].append(user_id)
        
        # write back to list
        with open('./src/config/blocklist.toml', 'w') as f:
            toml.dump(BLOCKLIST, f)

        # re-read config
        BLOCKLIST = toml.load("./src/config/blocklist.toml")
        BLOCKED_USERS = BLOCKLIST["blocked"]["users"]

        await ctx.response.send_message(f'Added {user} to blocklist!')

@bot.tree.command(name="unblock", description="Unblock a user")
@app_commands.describe(user = "Target User")
async def unblock(ctx: discord.Interaction, user: str):
    global BLOCKLIST
    global BLOCKED_USERS
    if not ctx.user.id in ADMINS:
        await ctx.response.send_message(f'You are not an admin!')
    else:
        user_id = int(re.search(r'\d+', user).group())

        if user_id in BLOCKLIST["blocked"]["users"]:
            BLOCKLIST["blocked"]["users"].remove(user_id)

        with open('./src/config/blocklist.toml', 'w') as f:
            toml.dump(BLOCKLIST, f)

        BLOCKLIST = toml.load("./src/config/blocklist.toml")
        BLOCKED_USERS = BLOCKLIST["blocked"]["users"]

        await ctx.response.send_message(f'Removed {user} from blocklist!')

### MISC ###

@bot.tree.command(name="version", description="Print Current Version")
async def version(ctx):
    await ctx.response.send_message(f'```Current Version: "{TAG}"```')
