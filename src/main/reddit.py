import toml
import os
import uuid
import requests
import aiohttp
import subprocess
from discord import File as dF

# Load the config.toml file
CONFIG = toml.load("./src/config/config.toml")

# Extract the client ID and client secret and agent from the config file
ID = CONFIG["reddit"]["client_id"]
SECRET = CONFIG["reddit"]["client_secret"]
AGENT = CONFIG["reddit"]["client_secret"]

# fixed API timespan declarations
TIMESPANS = ["all", "day", "hour", "month", "week", "year"]

# request headers
HEADERS = {
    'User-Agent': AGENT,
}

# check if sub even exists and if it's nsfw
async def check_sub(sub: str):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f'https://www.reddit.com/r/{sub}/about.json',
                headers=HEADERS
            ) as response:
                data = await response.json()
            if data['data']['over18']:
                return [True, True]
            else:
                return [True, False]
    except:
        return False

# perform the fetch on the sub
async def perform_fetch(sub: str, count: int, time: str):
    image_urls = []
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f'https://www.reddit.com/r/{sub}/top.json?limit=50&t={time}',
                headers=HEADERS
            ) as response:
                data = await response.json()
    except:
        return False
    for post in data['data']['children']:
        url = post['data']['url']
        if url.endswith((
            ".jpg",
            ".jpeg",
            ".png"
        )) and len(image_urls) < count: 
            image_urls.append(url)
    return image_urls

# prepare image for the bot
async def ready_image(img: str, needs_spoiler: bool):
    try:
        # get file ending
        file_ext = img.split(".")[-1]
        # fetch the image
        async with aiohttp.ClientSession() as session:
            async with session.get(
                img,
                headers=HEADERS
            ) as response:
                data = await response.read()
        # get path with uuid
        IMG_UUID = uuid.uuid4()
        IMG_PATH = os.path.join(f"{os.getcwd()}/data", f"{IMG_UUID}.{file_ext}")
        # write response to file
        with open(IMG_PATH, "wb") as f:
            f.write(data)
        # downscale with qds
        subprocess.Popen([
            "./src/bin/qds",
            "--image",
            IMG_PATH
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).wait()
        # remove original file
        os.remove(IMG_PATH)
        # get path
        FILE_PATH = os.path.join(f"{os.getcwd()}/data", f"qds_procd_{IMG_UUID}.{file_ext}")
        # open the file and return it as discord file to send
        with open(FILE_PATH, "rb") as f:
            picture = dF(f, spoiler=needs_spoiler, filename=f"{IMG_UUID}.{file_ext}")
        # remove and return
        os.remove(FILE_PATH)
        return picture
    except:
        return False
