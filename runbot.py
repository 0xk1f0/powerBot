#!./env/bin/python3

from src.bot import bot
import toml

# Load the config.toml and version file
config = toml.load("config.toml")
version = toml.load("VERSION")

# Extract token from config
TOKEN = config["discord"]["bot_token"]

# Print hello message
print(f"""
Starting v{version["tag"]}...

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
