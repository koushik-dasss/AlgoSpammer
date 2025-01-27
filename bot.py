from pyrogram import Client, filters
import asyncio
from dotenv import load_dotenv
from pyrogram.errors import FloodWait
import os
import logging
import re
from flask import Flask


load_dotenv()

API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")


if not API_ID or not API_HASH or not BOT_TOKEN:
    raise ValueError("Missing API credentials! Check your .env file.")


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)


web_app = Flask(__name__)

@web_app.route('/')
def home():
    return "Telegram bot is running!"


@app.on_message(filters.command(["start", "test"]))
async def start(client, message):
    await message.reply_text("I am alive")

MAX_SPAM_COUNT = 50


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

def run_flask():
    web_app.run(host="0.0.0.0", port=5000)

if __name__ == "__main__":
    logger.info("Bot is running...")
    import threading
    threading.Thread(target=run_flask).start()
    app.run()
