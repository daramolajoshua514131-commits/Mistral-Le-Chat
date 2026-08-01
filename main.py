import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from openai import OpenAI

# Load local .env file if present
load_dotenv()

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

SYSTEM_PROMPT = """
You are a helpful, versatile, and highly intelligent Telegram AI assistant.
Your capabilities include chatting, answering questions, writing, summarizing, 
translating, and brainstorming. Be clear, accurate, and concise.
"""

client = None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sends a welcome message on /start."""
    welcome_text = (
        "👋 **Hello! I am your AI Assistant.**\n\n"
        "Send me a message to start chatting, translating, writing, or summarizing!"
    )
    await update.message.reply_text(welcome_text, parse_mode="Markdown")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processes user text through OpenAI's API."""
    user_input = update.message.text
    
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_input},
            ],
            temperature=0.7,
        )
        ai_reply = response.choices[0].message.content
        await update.message.reply_text(ai_reply, parse_mode="Markdown")

    except Exception as e:
        logging.error(f"Error handling request: {e}")
        await update.message.reply_text(
            "⚠️ Sorry, an error occurred while processing your request. Please try again."
        )

if __name__ == "__main__":
    # Fetch environment variables and strip surrounding whitespace/quotes
    raw_telegram = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    raw_openai = os.environ.get("OPENAI_API_KEY", "")

    telegram_token = raw_telegram.strip().strip("'\"")
    openai_key = raw_openai.strip().strip("'\"")

    # Diagnostic logging for Railway environment debugging
    print(f"[DEBUG] TELEGRAM_BOT_TOKEN set: {bool(telegram_token)}")
    print(f"[DEBUG] OPENAI_API_KEY set: {bool(openai_key)}")

    if not telegram_token:
        logging.critical("❌ Error: TELEGRAM_BOT_TOKEN variable is not set in Environment Variables.")
        exit(1)

    if not openai_key:
        logging.critical("❌ Error: OPENAI_API_KEY variable is not set in Environment Variables.")
        exit(1)

    # Initialize OpenAI client with sanitized key
    client = OpenAI(api_key=openai_key)

    # Build and start Telegram bot
    app = ApplicationBuilder().token(telegram_token).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🚀 Bot is up and running...")
    app.run_polling(drop_pending_updates=True)
