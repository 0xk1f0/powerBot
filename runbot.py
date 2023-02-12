#!./env/bin/python3

from src.bot import bot
import toml

# Load the config.toml file
config = toml.load("config.toml")

# Extract token from config
TOKEN = config["discord"]["bot_token"]

# run this sht
bot.run(TOKEN)
