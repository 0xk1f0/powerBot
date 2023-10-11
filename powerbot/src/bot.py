import os
import discord
import toml
import re
from aiohttp import ClientSession, TCPConnector
from discord.ext import commands, tasks
from discord import app_commands
from datetime import datetime
from powerbot.src.helpers import access_check
from powerbot.src.integrations.reddit import (
    perform_fetch,
    save_units,
    check_sub,
    TIMESPANS,
)
from powerbot.src.integrations.wfp import (
    get_wfps,
    SFW_CATEGORIES,
    NSFW_CATEGORIES,
    TYPES,
)
from powerbot.src.integrations.macvendor import get_mac_vendor, check_MAC
from powerbot.src.integrations.conversion import (
    sha_checksum,
    md5_checksum,
    base_encode,
    base_decode,
)

# Set config path
CFG_PATH = os.getenv("CONF_PATH") or "/var/lib/powerBot/config"
# Read the version
VERSION = toml.load("VERSION")
# Data path for cache
DATA_PATH = os.getenv("CONF_PATH") or "/var/lib/powerBot/data"

# bot intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
# Create a bot object
bot = commands.Bot(command_prefix="/", intents=intents)
# client session
client_session = None


### ON READY ###


# initialize bot
@bot.event
async def on_ready():
    CFG = toml.load(os.path.join(CFG_PATH, "config.toml"))
    # sync
    try:
        await bot.tree.sync()
    except Exception as e:
        print(e)
    # set presence
    await bot.change_presence(activity=discord.Game(CFG["general"]["status"]))
    # new aiohttp session
    global client_session
    client_session = ClientSession(connector=TCPConnector(limit=20))
    # set daily task
    daily_ticker.start()


### TASKS ###


# this is for the daily action to take place
@tasks.loop(seconds=60)
async def daily_ticker():
    NOW = datetime.now()
    CFG = toml.load(os.path.join(CFG_PATH, "config.toml"))
    if NOW.hour == 12 and NOW.minute == 1:
        await bot.wait_until_ready()
        channel = await bot.fetch_channel(CFG["discord"]["daily_channel"])
        result = await perform_fetch(
            CFG["discord"]["daily_sub"],
            int(CFG["discord"]["daily_count"]),
            "day",
            (".jpg", ".jpeg", ".png"),
            client_session,
        )
        if result != False and len(result) != 0:
            await channel.send(
                f"Time for r/{CFG['discord']['daily_sub']} Daily Top {int(CFG['discord']['daily_count'])}!"
            )
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
            await channel.send(f"{CFG['general']['err']}")


### EVENTS ###


@bot.event
async def on_message(message):
    CFG = toml.load(os.path.join(CFG_PATH, "config.toml"))
    LIST = CFG["triggers"]["list"]
    for item in LIST:
        if item[0] in str(message.content).lower() and message.author != bot.user:
            await message.channel.send(item[1])
            return
    await bot.process_commands(message)


### MAIN ###


@bot.tree.command(name="top", description="/top <subreddit> <timespan> <count>")
@app_commands.describe(subreddit="Target Subreddit")
@app_commands.describe(timespan=f"Timespan: {TIMESPANS}")
@app_commands.describe(count="Image Count")
async def top(ctx: discord.Interaction, subreddit: str, timespan: str, count: int):
    CFG = toml.load(os.path.join(CFG_PATH, "config.toml"))
    HAS_ACCESS = access_check(
        ctx.user.id, CFG["general"]["admins"], CFG["general"]["blocked"], False
    )
    if HAS_ACCESS != True:
        await ctx.response.send_message(HAS_ACCESS)
        return
    if timespan not in TIMESPANS:
        await ctx.response.send_message(f"Invalid Timespan, try one of: {TIMESPANS}")
    elif count > int(CFG["reddit"]["fetch_cap"]):
        await ctx.response.send_message(
            f"Max Count is capped to {CFG['reddit']['fetch_cap']}!"
        )
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
                (".jpg", ".jpeg", ".png", ".gif", ".mp4"),
                client_session,
            )
            if result != False and len(result) != 0:
                await ctx.followup.send(
                    f"Top {count}/{timespan} images from r/{subreddit}"
                )
                for unit in result:
                    if unit[1] == True:
                        await ctx.channel.send(f"|| {unit[0]} ||")
                    else:
                        await ctx.channel.send(unit[0])
            else:
                await ctx.followup.send(f"{CFG['general']['err']}")


@bot.tree.command(name="wfp", description="/wfp <type> <category> <count>")
@app_commands.describe(type=f"Type: {TYPES}")
@app_commands.describe(category=f"Image Category: {SFW_CATEGORIES + NSFW_CATEGORIES}")
@app_commands.describe(count="Image Count")
async def wfp(ctx: discord.Interaction, type: str, category: str, count: int):
    CFG = toml.load(os.path.join(CFG_PATH, "config.toml"))
    HAS_ACCESS = access_check(
        ctx.user.id, CFG["general"]["admins"], CFG["general"]["blocked"], False
    )
    if HAS_ACCESS != True:
        await ctx.response.send_message(HAS_ACCESS)
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
    elif count > int(CFG["reddit"]["fetch_cap"]):
        await ctx.response.send_message(
            f"Max Count is capped to {CFG['reddit']['fetch_cap']}!"
        )
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
            await ctx.followup.send(f"{CFG['general']['err']}")


@bot.tree.command(name="mac", description="/mac <address>")
@app_commands.describe(mac="A valid MAC Address")
async def mac(ctx: discord.Interaction, mac: str):
    CFG = toml.load(os.path.join(CFG_PATH, "config.toml"))
    HAS_ACCESS = access_check(
        ctx.user.id, CFG["general"]["admins"], CFG["general"]["blocked"], False
    )
    if HAS_ACCESS != True:
        await ctx.response.send_message(HAS_ACCESS)
        return
    # check validity else proceed
    if not check_MAC(mac):
        await ctx.response.send_message("That MAC just doesn't look right..")
        return
    else:
        await ctx.response.defer()
        result = await get_mac_vendor(mac, client_session)
        if result != False or None:
            await ctx.followup.send(f"MAC belongs to: {result}")
        else:
            await ctx.followup.send(f"{CFG['general']['err']}")


### CONVERSION ###


@bot.tree.command(name="shasum", description="Calculate shasum")
@app_commands.describe(input="Input String")
@app_commands.describe(
    algorithm="Either 'sha1sum', 'sha224', 'sha256', 'sha384' or 'sha512'"
)
async def shasum(ctx: discord.Interaction, input: str, algorithm: str):
    CFG = toml.load(os.path.join(CFG_PATH, "config.toml"))
    HAS_ACCESS = access_check(
        ctx.user.id, CFG["general"]["admins"], CFG["general"]["blocked"], False
    )
    if HAS_ACCESS != True:
        await ctx.response.send_message(HAS_ACCESS)
        return
    if algorithm not in ("sha1sum", "sha224", "sha256", "sha384", "sha512"):
        await ctx.response.send_message("Invalid Algorithm")
    else:
        await ctx.response.defer()
        CHECKSUM = sha_checksum(input, algorithm)
        if CHECKSUM == False:
            await ctx.followup.send(f"{CFG['general']['err']}")
        else:
            await ctx.followup.send(f"```{CHECKSUM}```")


@bot.tree.command(name="md5sum", description="Calculate md5sum")
@app_commands.describe(input="Input String")
async def md5sum(ctx: discord.Interaction, input: str):
    CFG = toml.load(os.path.join(CFG_PATH, "config.toml"))
    HAS_ACCESS = access_check(
        ctx.user.id, CFG["general"]["admins"], CFG["general"]["blocked"], False
    )
    if HAS_ACCESS != True:
        await ctx.response.send_message(HAS_ACCESS)
        return
    await ctx.response.defer()
    CHECKSUM = md5_checksum(input)
    if CHECKSUM == False:
        await ctx.followup.send(f"{CFG['general']['err']}")
    else:
        await ctx.followup.send(f"```{CHECKSUM}```")


@bot.tree.command(name="baseenc", description="Encode baseX")
@app_commands.describe(input="Input String")
@app_commands.describe(type="Either 'base32' or 'base64'")
async def baseenc(ctx: discord.Interaction, input: str, type: str):
    CFG = toml.load(os.path.join(CFG_PATH, "config.toml"))
    HAS_ACCESS = access_check(
        ctx.user.id, CFG["general"]["admins"], CFG["general"]["blocked"], False
    )
    if HAS_ACCESS != True:
        await ctx.response.send_message(HAS_ACCESS)
        return
    if type not in ("base32", "base64"):
        await ctx.response.send_message("Invalid Type")
    else:
        await ctx.response.defer()
        CHECKSUM = base_encode(input, type)
        if CHECKSUM == False:
            await ctx.followup.send(f"{CFG['general']['err']}")
        else:
            await ctx.followup.send(f"```{CHECKSUM}```")


@bot.tree.command(name="basedec", description="Decode baseX")
@app_commands.describe(input="Input String")
@app_commands.describe(type="Either 'base32' or 'base64'")
async def basedec(ctx: discord.Interaction, input: str, type: str):
    CFG = toml.load(os.path.join(CFG_PATH, "config.toml"))
    HAS_ACCESS = access_check(
        ctx.user.id, CFG["general"]["admins"], CFG["general"]["blocked"], False
    )
    if HAS_ACCESS != True:
        await ctx.response.send_message(HAS_ACCESS)
        return
    if type not in ("base32", "base64"):
        await ctx.response.send_message("Invalid Type")
    else:
        await ctx.response.defer()
        CHECKSUM = base_decode(input, type)
        if CHECKSUM == False:
            await ctx.followup.send(f"{CFG['general']['err']}")
        else:
            await ctx.followup.send(f"```{CHECKSUM}```")


### MODERATION ###


@bot.tree.command(name="purge", description="Delete the next x Messages")
@app_commands.describe(message_id="ID of the Message above Start")
@app_commands.describe(count="Number of Messages to Purge")
async def purge_reply(ctx: discord.Interaction, message_id: str, count: int):
    CFG = toml.load(os.path.join(CFG_PATH, "config.toml"))
    HAS_ACCESS = access_check(
        ctx.user.id, CFG["general"]["admins"], CFG["general"]["blocked"], True
    )
    if HAS_ACCESS != True:
        await ctx.response.send_message(HAS_ACCESS)
        return
    try:
        # fetch message by ID
        MESSAGE = await ctx.channel.fetch_message(message_id)
        # get the history after message id
        HISTORY = [
            message async for message in ctx.channel.history(after=MESSAGE, limit=count)
        ]
        # delete it
        if HISTORY and len(HISTORY) > 0:
            await ctx.response.defer()
            await ctx.channel.delete_messages(HISTORY)
        else:
            await ctx.response.send_message("No Messages to delete!")
    except:
        await ctx.followup.send(f"{CFG['general']['err']}")
    finally:
        await ctx.followup.send(f"Deleted {len(HISTORY)} message/s!")


@bot.tree.command(name="block", description="Block a user")
@app_commands.describe(user="Target User")
async def block(ctx: discord.Interaction, user: str):
    CFG = toml.load(os.path.join(CFG_PATH, "config.toml"))
    HAS_ACCESS = access_check(
        ctx.user.id, CFG["general"]["admins"], CFG["general"]["blocked"], True
    )
    if HAS_ACCESS != True:
        await ctx.response.send_message(HAS_ACCESS)
        return
    else:
        # convert to normal id
        user_id = int(re.search(r"\d+", user).group())

        # check if user is not blocked already -> block
        if not user_id in CFG["general"]["blocked"]:
            CFG["general"]["blocked"].append(user_id)

        # write back to list
        with open(os.path.join(CFG_PATH, "config.toml"), "w") as f:
            toml.dump(CFG, f)

        await ctx.response.send_message(f"Added {user} to blocklist!")


@bot.tree.command(name="unblock", description="Unblock a user")
@app_commands.describe(user="Target User")
async def unblock(ctx: discord.Interaction, user: str):
    CFG = toml.load(os.path.join(CFG_PATH, "config.toml"))
    HAS_ACCESS = access_check(
        ctx.user.id, CFG["general"]["admins"], CFG["general"]["blocked"], True
    )
    if HAS_ACCESS != True:
        await ctx.response.send_message(HAS_ACCESS)
        return
    else:
        user_id = int(re.search(r"\d+", user).group())

        if user_id in CFG["general"]["blocked"]:
            CFG["general"]["blocked"].remove(user_id)

        with open(os.path.join(CFG_PATH, "config.toml"), "w") as f:
            toml.dump(CFG, f)

        await ctx.response.send_message(f"Removed {user} from blocklist!")


### MISC ###


@bot.tree.command(name="addtrigger", description="Add a new Triggerword")
@app_commands.describe(trigger="Triggerword to add")
@app_commands.describe(response="Trigger response")
async def add_trigger(ctx: discord.Interaction, trigger: str, response: str):
    CFG = toml.load(os.path.join(CFG_PATH, "config.toml"))
    HAS_ACCESS = access_check(
        ctx.user.id, CFG["general"]["admins"], CFG["general"]["blocked"], True
    )
    if HAS_ACCESS != True:
        await ctx.response.send_message(HAS_ACCESS)
        return
    else:
        for item in CFG["triggers"]["list"]:
            if trigger == item[0]:
                # word exists
                await ctx.response.send_message(f'Trigger "{trigger}" already exists!')
                return
        CFG["triggers"]["list"].append([trigger, response])
        # write back to list
        with open(os.path.join(CFG_PATH, "config.toml"), "w") as f:
            toml.dump(CFG, f)

        await ctx.response.send_message(f'Added "{trigger}" to Triggerwords!')


@bot.tree.command(name="removetrigger", description="Remove a Triggerword")
@app_commands.describe(trigger="Triggerword to remove")
async def remove_trigger(ctx: discord.Interaction, trigger: str):
    CFG = toml.load(os.path.join(CFG_PATH, "config.toml"))
    HAS_ACCESS = access_check(
        ctx.user.id, CFG["general"]["admins"], CFG["general"]["blocked"], True
    )
    if HAS_ACCESS != True:
        await ctx.response.send_message(HAS_ACCESS)
        return
    else:
        for item in CFG["triggers"]["list"]:
            if trigger == item[0]:
                CFG["triggers"]["list"].remove(item)
                # write back to list
                with open(os.path.join(CFG_PATH, "config.toml"), "w") as f:
                    toml.dump(CFG, f)
                await ctx.response.send_message(f'Removed "{trigger}" from Triggerwords!')
                return
        # word doesnt exist
        await ctx.response.send_message(f'Trigger "{trigger}" doesn\'t exists!')


@bot.tree.command(name="version", description="Print Current Version")
async def version(ctx):
    CFG = toml.load(os.path.join(CFG_PATH, "config.toml"))
    HAS_ACCESS = access_check(
        ctx.user.id, CFG["general"]["admins"], CFG["general"]["blocked"], False
    )
    if HAS_ACCESS != True:
        await ctx.response.send_message(HAS_ACCESS)
        return
    else:
        await ctx.response.send_message(f'```Current Version: "{VERSION["tag"]}"```')
