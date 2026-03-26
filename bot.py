"""
Ethiopic Bible Telegram Bot

Delivers Bible verses on command and on schedule (morning & evening).

Setup:
  1. Create a bot via @BotFather on Telegram, copy the token
  2. Set the token:  export TELEGRAM_BOT_TOKEN="your-token-here"
  3. Run:  python bot.py
  4. Open your bot in Telegram and type /start

Scheduled verses are sent to all users who have typed /subscribe.
"""

import os
import logging
import httpx
from datetime import time, datetime, timedelta

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

from bible_data import (
    load_all_books,
    get_all_book_names,
    get_book,
    get_random_verse,
    get_daily_verse,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
RENDER_URL = os.environ.get("RENDER_EXTERNAL_URL", "")  # set automatically by Render
KEEP_ALIVE_INTERVAL = 10 * 60  # 10 minutes in seconds

# Simple file-based subscriber persistence
SUBSCRIBERS_FILE = os.path.join(os.path.dirname(__file__), "subscribers.txt")


def _load_subscribers() -> set[int]:
    """Load subscriber chat IDs from disk."""
    if not os.path.isfile(SUBSCRIBERS_FILE):
        return set()
    with open(SUBSCRIBERS_FILE, "r") as f:
        return {int(line.strip()) for line in f if line.strip()}


def _save_subscribers(chat_ids: set[int]):
    """Save subscriber chat IDs to disk."""
    with open(SUBSCRIBERS_FILE, "w") as f:
        for cid in sorted(chat_ids):
            f.write(f"{cid}\n")


subscribers: set[int] = set()


# ─── Formatting helper ────────────────────────────────────────────────

def format_verse(v: dict) -> str:
    """Format a verse dict into a nice Telegram message."""
    return (
        f"📖 *{v['book']}* {v['chapter']}:{v['verse_number']}\n\n"
        f"_{v['text']}_"
    )


# ─── Command handlers ─────────────────────────────────────────────────

async def start_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Welcome message with available commands."""
    await update.message.reply_text(
        "✝️ *የኢትዮጵያ መጽሐፍ ቅዱስ ቦት*\n"
        "Ethiopic Bible Bot\n\n"
        "Commands:\n"
        "/verse — Random verse\n"
        "/daily — Today's verse\n"
        "/books — Browse books\n"
        "/subscribe — Get morning & evening verses\n"
        "/unsubscribe — Stop scheduled verses\n"
        "/help — Show this message",
        parse_mode="Markdown",
    )


async def help_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await start_cmd(update, ctx)


async def verse_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Send a random verse."""
    v = get_random_verse()
    await update.message.reply_text(format_verse(v), parse_mode="Markdown")


async def daily_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Send today's deterministic verse."""
    day_number = (datetime.utcnow() - datetime(2024, 1, 1)).days
    v = get_daily_verse(day_number)
    await update.message.reply_text(
        f"🌅 *Verse of the Day*\n\n{format_verse(v)}",
        parse_mode="Markdown",
    )


async def books_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Show paginated book list as inline buttons (10 per page)."""
    await _send_book_page(update.message, page=0)


async def _send_book_page(target, page: int):
    """Send a page of book buttons."""
    names = get_all_book_names()
    page_size = 10
    start = page * page_size
    page_names = names[start : start + page_size]
    total_pages = (len(names) + page_size - 1) // page_size

    buttons = [
        [InlineKeyboardButton(name, callback_data=f"book:{name}")]
        for name in page_names
    ]
    # Navigation row
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("⬅️ Prev", callback_data=f"page:{page - 1}"))
    if page < total_pages - 1:
        nav.append(InlineKeyboardButton("Next ➡️", callback_data=f"page:{page + 1}"))
    if nav:
        buttons.append(nav)

    await target.reply_text(
        f"📚 *Books* (page {page + 1}/{total_pages})\nTap a book to get a random verse from it:",
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode="Markdown",
    )


async def subscribe_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Subscribe to morning & evening verses."""
    chat_id = update.effective_chat.id
    subscribers.add(chat_id)
    _save_subscribers(subscribers)
    await update.message.reply_text(
        "✅ Subscribed! You'll receive verses at *6:00 AM* and *8:00 PM* (UTC).",
        parse_mode="Markdown",
    )


async def unsubscribe_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Unsubscribe from scheduled verses."""
    chat_id = update.effective_chat.id
    subscribers.discard(chat_id)
    _save_subscribers(subscribers)
    await update.message.reply_text("🔕 Unsubscribed from scheduled verses.")


# ─── Callback query handler (inline buttons) ──────────────────────────

async def button_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("page:"):
        page = int(data.split(":")[1])
        # Edit the existing message with the new page
        names = get_all_book_names()
        page_size = 10
        start = page * page_size
        page_names = names[start : start + page_size]
        total_pages = (len(names) + page_size - 1) // page_size

        buttons = [
            [InlineKeyboardButton(name, callback_data=f"book:{name}")]
            for name in page_names
        ]
        nav = []
        if page > 0:
            nav.append(InlineKeyboardButton("⬅️ Prev", callback_data=f"page:{page - 1}"))
        if page < total_pages - 1:
            nav.append(InlineKeyboardButton("Next ➡️", callback_data=f"page:{page + 1}"))
        if nav:
            buttons.append(nav)

        await query.edit_message_text(
            f"📚 *Books* (page {page + 1}/{total_pages})\nTap a book to get a random verse from it:",
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode="Markdown",
        )

    elif data.startswith("book:"):
        book_name = data.split(":", 1)[1]
        book = get_book(book_name)
        if not book:
            await query.edit_message_text("Book not found.")
            return
        # Pick a random verse from this book
        import random
        chapter = random.choice(book["chapters"])
        verse_idx = random.randrange(len(chapter["verses"]))
        v = {
            "book": book["title"],
            "chapter": chapter["chapter"],
            "verse_number": verse_idx + 1,
            "text": chapter["verses"][verse_idx],
        }
        await query.edit_message_text(format_verse(v), parse_mode="Markdown")


# ─── Scheduled jobs ───────────────────────────────────────────────────

async def send_morning_verse(ctx: ContextTypes.DEFAULT_TYPE):
    """Send morning verse to all subscribers."""
    day_number = (datetime.utcnow() - datetime(2024, 1, 1)).days
    v = get_daily_verse(day_number * 2)  # even offset for morning
    text = f"🌅 *Good Morning!*\n\n{format_verse(v)}"
    await _broadcast(ctx, text)


async def send_evening_verse(ctx: ContextTypes.DEFAULT_TYPE):
    """Send evening verse to all subscribers."""
    day_number = (datetime.utcnow() - datetime(2024, 1, 1)).days
    v = get_daily_verse(day_number * 2 + 1)  # odd offset for evening
    text = f"🌙 *Good Evening!*\n\n{format_verse(v)}"
    await _broadcast(ctx, text)


async def _broadcast(ctx: ContextTypes.DEFAULT_TYPE, text: str):
    """Send a message to all subscribers, removing any that blocked the bot."""
    failed = set()
    for chat_id in subscribers.copy():
        try:
            await ctx.bot.send_message(chat_id=chat_id, text=text, parse_mode="Markdown")
        except Exception as e:
            logger.warning("Failed to send to %s: %s", chat_id, e)
            failed.add(chat_id)
    if failed:
        subscribers.difference_update(failed)
        _save_subscribers(subscribers)


# ─── Keep-alive ping ──────────────────────────────────────────────────

async def keep_alive_ping(ctx: ContextTypes.DEFAULT_TYPE):
    """Ping our own /health endpoint to prevent Render free tier from sleeping."""
    if not RENDER_URL:
        return
    url = f"{RENDER_URL}/health"
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, timeout=10)
            logger.info("Keep-alive ping %s → %s", url, resp.status_code)
    except Exception as e:
        logger.warning("Keep-alive ping failed: %s", e)


# ─── Main ─────────────────────────────────────────────────────────────

def main():
    if not TOKEN:
        print("ERROR: Set TELEGRAM_BOT_TOKEN environment variable.")
        print("  1. Message @BotFather on Telegram to create a bot")
        print("  2. Copy the token")
        print('  3. Run: export TELEGRAM_BOT_TOKEN="your-token-here"')
        print("  4. Then run this script again")
        return

    # Load Bible data
    load_all_books()

    # Load saved subscribers
    subscribers.update(_load_subscribers())
    logger.info("Loaded %d subscribers", len(subscribers))

    # Build bot application
    app = Application.builder().token(TOKEN).build()

    # Register command handlers
    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("verse", verse_cmd))
    app.add_handler(CommandHandler("daily", daily_cmd))
    app.add_handler(CommandHandler("books", books_cmd))
    app.add_handler(CommandHandler("subscribe", subscribe_cmd))
    app.add_handler(CommandHandler("unsubscribe", unsubscribe_cmd))
    app.add_handler(CallbackQueryHandler(button_handler))

    # Schedule morning (6:00 UTC) and evening (20:00 UTC) verses
    job_queue = app.job_queue
    job_queue.run_daily(send_morning_verse, time=time(hour=6, minute=0))
    job_queue.run_daily(send_evening_verse, time=time(hour=20, minute=0))

    # Keep-alive: ping /health every 10 min to prevent Render free tier sleep
    if RENDER_URL:
        job_queue.run_repeating(
            keep_alive_ping,
            interval=timedelta(seconds=KEEP_ALIVE_INTERVAL),
            first=timedelta(seconds=30),  # first ping 30s after startup
        )
        logger.info("Keep-alive enabled — pinging %s/health every %ds", RENDER_URL, KEEP_ALIVE_INTERVAL)

    logger.info("Bot starting — scheduled verses at 06:00 and 20:00 UTC")
    app.run_polling()


if __name__ == "__main__":
    main()
