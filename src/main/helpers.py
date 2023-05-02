import re
import random
from PIL import Image

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
