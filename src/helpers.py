import re
import random
from PIL import Image

# GIF List of hugs
HUGLIST = [
    "https://tenor.com/view/hug-gif-25588769",
    "https://tenor.com/view/rezero-rem-subaru-felix-subaru-felix-gif-25285761",
    "https://tenor.com/view/anime-hug-sweet-love-gif-14246498"
]

# GIF List of shoot
SHOOTLIST = [
    "https://tenor.com/view/anime-gun-gunslinger-girl-henrietta-gif-13064976",
    "https://tenor.com/view/guns-anime-shoot-gif-15538806",
    "https://tenor.com/view/nichijou-minigun-comedy-anime-fuck-you-gif-14778256"
]

# check for valid spotify URL using regular expression
def is_valid_url(url):
    regex = re.compile(r'^https://open\.spotify\.com/playlist/.+$')
    return re.match(regex, url) is not None

# compress input image using the PIL
def compress(file_extension: str, path: str, image: str):
    match(file_extension):
        case "jpg" | "jpeg" | "png":
            with Image.open(f"{path}{image}") as in_img:
                in_img.save(
                    f"{path}proc_{image}",
                    optimize=True,
                    quality=80
                )
        case _:
            return
    return

# react with gif based on input type
def gifReact(type):
    match type:
        case "hug":
            return random.choice(HUGLIST)
        case "shoot":
            return random.choice(SHOOTLIST)
