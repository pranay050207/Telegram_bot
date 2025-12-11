import os
from os import environ

# --- Bot information (Loaded from Render/Railway Environment Variables) ---
# The second value is the default (e.g., 'Media_search', or empty string)

SESSION = environ.get('SESSION', 'Media_search')
# API_ID and API_HASH are required if your bot uses Telethon or Pyrogram
try:
    API_ID = int(environ.get('API_ID', '37133585'))
except ValueError:
    API_ID = 0  # Default to 0 if not set or invalid
    
API_HASH = environ.get('API_HASH', 'b054d86be1d63b35e8054b7f5342e7bd')
BOT_TOKEN = environ.get('BOT_TOKEN', '8567624597:AAHcPd3aLAgRi3ax6KxubQC815-P4_e1QIM') # Your token from BotFather


# --- Other Bot Settings ---

# Post (Example from your screenshot)
PMMS = environ.get('PMMS', 'PMMS') 

# Bot settings (Example from your screenshot)
try:
    CACHE_TIME = int(environ.get('CACHE_TIME', 300))
except ValueError:
    CACHE_TIME = 300

USE_CAPTION_FILTER = environ.get('USE_CAPTION_FILTER', 'False').lower() in ('true', 'yes', '1')

# This complex line requires careful configuration based on your actual code structure.
PICS = environ.get('PICS', 'https://telegra.ph/file/b806ad31add1ea1557h8w.jpg').split() 

# Admins, Channels & Users (Assuming comma or space separated lists)
ADMINS = [int(x) for x in environ.get("ADMINS", '5685227455').split()] 
CHANNELS = [int(i) for i in environ.get("CHANNELS", '').split()]
