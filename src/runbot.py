#!./env/bin/python3

from main.bot import bot
import toml

# Load the config.toml and version file
CONFIG = toml.load("./src/config/config.toml")
VERSION = toml.load("VERSION")

# Extract token from config
TOKEN = CONFIG["discord"]["bot_token"]
TAG = VERSION["tag"]

# Print hello message
print(f"""
Starting v{TAG}...

                              ____        _   
 _ __   _____      _____ _ __| __ )  ___ | |_ 
| '_ \ / _ \ \ /\ / / _ \ '__|  _ \ / _ \| __|
| |_) | (_) \ V  V /  __/ |  | |_) | (_) | |_ 
| .__/ \___/ \_/\_/ \___|_|  |____/ \___/ \__|
|_|

~ by 0xk1f0
""")

# Run this sht
bot.run(TOKEN)
