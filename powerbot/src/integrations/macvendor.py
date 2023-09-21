import aiohttp
from urllib.parse import quote as urlencode
import re

# pattern to match
MAC_PATTERN = r"^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$"

# check if a mac address is valid


def check_MAC(input: str):
    if re.search(MAC_PATTERN, input):
        return True
    else:
        return False


async def get_mac_vendor(mac: str, session: aiohttp.ClientSession):
    try:
        async with session.get(
            f"https://api.macvendors.com/{urlencode(mac)}"
        ) as response:
            data = await response.text()
    except:
        return False
    if data:
        return data
    else:
        return False
