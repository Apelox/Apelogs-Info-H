import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
COMMAND_PREFIX = "+"
API_WEATHER=os.getenv('API_WEATHER')
API_FILME=os.getenv('API_FILME')