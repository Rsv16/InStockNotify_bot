import asyncio
import logging
import os
import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import Application, CommandHandler

TOKEN = os.getenv("7791800424:AAFBRTy00LVoU2hZPw_euGu1UOIu1GsaoBc")  # Read token from environment variable
CHECK_INTERVAL = 300  # 5 minutes

user_urls = {}  # Store user-specific URLs

logging.basicConfig(level=logging.INFO)


async def start(update: Update, context) -> None:
    await update.message.reply_text("Send a URL to monitor its stock status.\nUsage: /track <url>")


async def check_stock(url: str) -> bool:
    """Check if 'Out Of Stock' is present on the page."""
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        return "Out Of Stock" not in soup.get_text()
    except Exception as e:
        logging.error(f"Error fetching {url}: {e}")
        return False


async def add_url(update: Update, context) -> None:
    """User sends a URL, and it's added to tracking."""
    if context.args:
        url = context.args[0]
        user_id = update.message.chat_id
        user_urls[user_id] = url
        await update.message.reply_text(f"Tracking stock status for: {url}")
    else:
        await update.message.reply_text("Please provide a URL. Example: /track https://example.com/product")


async def monitor_stock():
    """Continuously check URLs every 5 minutes."""
    while True:
        for user_id, url in list(user_urls.items()):
            if await check_stock(url):
                await app.bot.send_message(user_id, f"The product at {url} is now in stock!")
                del user_urls[user_id]  # Stop tracking after notification
        await asyncio.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("track", add_url))

    loop = asyncio.get_event_loop()
    loop.create_task(monitor_stock())

    app.run_polling()