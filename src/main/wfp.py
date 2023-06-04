import aiohttp
import toml

# Load the config.toml file
CONFIG = toml.load("./src/config/config.toml")

# wfp specific things
TYPES = [ "sfw", "nsfw" ]
NSFW_CATEGORIES = [ "waifu", "neko", "trap", "blowjob" ]
SFW_CATEGORIES = [
    "waifu","neko","shinobu","megumin","bully","cuddle","cry","hug","awoo","kiss",
    "lick","pat","smug","bonk","yeet","blush","smile","wave","highfive","handhold",
    "nom","bite","glomp","slap","kill","kick","happy","wink","poke","dance","cringe"
]

# perform the fetch on the sub
async def get_wfps(type: str, category: int, count: int):
    units = []
    for i in range(0, count):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f'https://api.waifu.pics/{type}/{category}'
                ) as response:
                    data = await response.json()
        except:
            return False
        if data['url']:
            units.append([data['url'], type])
    return units
