from pyrogram import Client, filters
import asyncio
from dotenv import load_dotenv
from pyrogram.errors import FloodWait
import os
import logging
import re

# Load environment variables
load_dotenv()

API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Ensure credentials are loaded properly
if not API_ID or not API_HASH or not BOT_TOKEN:
    raise ValueError("Missing API credentials! Check your .env file.")

# Configure logging for better debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the bot client with your credentials
app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Respond to /start and /test commands
@app.on_message(filters.command(["start", "test"]))
async def start(client, message):
    await message.reply_text("I am alive")

# Maximum spam limit to avoid bans
MAX_SPAM_COUNT = 50

# Handle the !spam command with regex and async handling
@app.on_message(filters.text & filters.regex(r"^!spam (\d+) (.+)"))
async def spam(client, message):
    try:
        match = re.match(r"!spam (\d+) (.+)", message.text)
        if not match:
            await message.reply_text("Invalid command format. Use !spam <count> <message>")
            return
        
        count = int(match.group(1))
        text = match.group(2)

        if count > MAX_SPAM_COUNT:
            await message.reply_text(f"Limit exceeded! Max allowed is {MAX_SPAM_COUNT}.")
            return

        for _ in range(count):
            try:
                await message.reply_text(text)
                await asyncio.sleep(1.5)  # Delay to avoid hitting rate limits
            except FloodWait as e:
                logger.warning(f"Flood wait for {e.value} seconds")
                await asyncio.sleep(e.value)  # Sleep for the required flood wait duration

    except Exception as e:
        logger.error(f"Error: {e}")
        await message.reply_text(f"Error: {e}")

# Start the bot
logger.info("Bot is running...")
app.run()
