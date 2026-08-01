import os
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from openai import OpenAI

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# System prompt defining the AI assistant's capabilities
SYSTEM_PROMPT = """
You are a helpful, versatile, and highly intelligent Telegram AI assistant.
Your capabilities include chatting, answering questions, writing, summarizing, 
translating, and brainstorming. Be clear, accurate, and concise.
"""

# Declare client globally, initialized inside main
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
    telegram_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    openai_key = os.environ.get("OPENAI_API_KEY")

    # Validate environment variables before initializing SDKs
    if not telegram_token:
        raise ValueError("Missing TELEGRAM_BOT_TOKEN environment variable in Railway.")
    if not openai_key:
        raise ValueError("Missing OPENAI_API_KEY environment variable in Railway.")

    # Initialize client after key verification
    client = OpenAI(api_key=openai_key)

    # Build and start Telegram bot
    app = ApplicationBuilder().token(telegram_token).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot is up and running...")
    app.run_polling(drop_pending_updates=True)
