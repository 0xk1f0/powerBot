#!./env/bin/python3

import toml
from os import getenv, path
from powerbot.src.bot import bot

# Load the config.toml and version file
VERSION = toml.load("pyproject.toml")["tool"]["poetry"]["version"]
CONFIG = getenv("CONF_PATH") or "/var/lib/powerBot/config"
CONFIG = toml.load(path.join(CONFIG, "config.toml"))


def main():
    # Print hello message
    print(
        f"""
    Starting Version {VERSION}..

                                  ____        _   
     _ __   _____      _____ _ __| __ )  ___ | |_ 
    | '_ \ / _ \ \ /\ / / _ \ '__|  _ \ / _ \| __|
    | |_) | (_) \ V  V /  __/ |  | |_) | (_) | |_ 
    | .__/ \___/ \_/\_/ \___|_|  |____/ \___/ \__|
    |_|

    ~ by 0xk1f0
    """
    )
    # Run this sht
    bot.run(CONFIG["discord"]["bot_token"])
