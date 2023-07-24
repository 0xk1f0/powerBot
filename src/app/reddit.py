import toml
import os
import uuid
import aiohttp
import subprocess
from discord import File as dF
from base64 import b64encode

# Load the config.toml file
CONFIG = os.getenv('CONF_PATH') or '/var/lib/powerBot/config'
CONFIG = toml.load(os.path.join(CONFIG, 'config.toml'))

# data path for cache
DATA_PATH = os.getenv('CONF_PATH') or '/var/lib/powerBot/data'

# binary path for downscaler
DS_PATH = os.getenv('DS_PATH') or '/app/bin/qds'

# Extract the client ID and client secret and agent from the config file
ID = CONFIG["reddit"]["client_id"]
SECRET = CONFIG["reddit"]["client_secret"]
AGENT = CONFIG["reddit"]["user_agent"]

# fixed API timespan declarations
TIMESPANS = ["all", "day", "hour", "month", "week", "year"]

# request headers
HEADERS = {
    # i think it goes like this, reddit has terrible API docs
    'Authorization': f'Basic {b64encode(b"{ID}:{SECRET}")}',
    'User-Agent': AGENT
}

# check if sub even exists and if it's nsfw
async def check_sub(sub: str, session: aiohttp.ClientSession):
    try:
        async with session.get(
            f'https://www.reddit.com/r/{sub}/about.json',
            headers=HEADERS
        ) as response:
            if response.status == 200:
                return True
            else:
                return False
    except:
        return False

# perform the fetch on the sub
async def perform_fetch(sub: str, count: int, time: str, formats: tuple, session: aiohttp.ClientSession):
    units = []
    try:
        async with session.get(
            f'https://www.reddit.com/r/{sub}/top.json?limit=50&t={time}',
            headers=HEADERS
        ) as response:
            data = await response.json()
    except:
        return False
    for post in data['data']['children']:
        SPOILER_TAG = post['data']['over_18']
        URL = post['data']['url']
        if URL.endswith(formats) and len(units) < count: 
            units.append([URL, SPOILER_TAG])
    return units

# prepare image for the bot
async def save_units(img: str, needs_spoiler: bool, session: aiohttp.ClientSession):
    try:
        # get file ending
        file_ext = img.split(".")[-1]
        # fetch the image
        async with session.get(img,headers=HEADERS) as response:
            data = await response.read()
        # get path with uuid
        IMG_UUID = uuid.uuid4()
        IMG_PATH = os.path.join(DATA_PATH, f"{IMG_UUID}.{file_ext}")
        # write response to file
        with open(IMG_PATH, "wb") as f:
            f.write(data)
        # downscale with qds
        subprocess.run([
            DS_PATH,
            "--image",
            IMG_PATH
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        # get path
        FILE_PATH = os.path.join(DATA_PATH, f"qds_procd_{IMG_UUID}.{file_ext}")
        # open the file and return it as discord file to send
        with open(FILE_PATH, "rb") as f:
            picture = dF(f, spoiler=needs_spoiler)
        # remove processed file
        os.remove(FILE_PATH)
        return picture
    except:
        return False
