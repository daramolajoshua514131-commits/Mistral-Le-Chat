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

# Load environment variables
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# System prompt defining the AI assistant's multi-functional capabilities
SYSTEM_PROMPT = """
You are a helpful, versatile, and highly intelligent Telegram AI assistant.
Your capabilities include:
- Chatting & answering questions
- Writing essays, emails, stories, and code
- Summarizing text provided by the user
- Translating text across languages
- Brainstorming creative ideas
- Assisting with everyday personal & work tasks
Be clear, accurate, and concise. Use markdown formatting where appropriate.
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sends a welcome message on /start."""
    welcome_text = (
        "👋 **Hello! I am your AI Assistant.**\n\n"
        "I can help you with:\n"
        "• 💬 **Chatting & Answering Questions**\n"
        "• ✍️ **Writing & Drafting** (Emails, Posts, Essays)\n"
        "• 📝 **Summarizing** long texts or articles\n"
        "• 🌐 **Translating** between languages\n"
        "• 💡 **Brainstorming** ideas & problem solving\n"
        "• 🛠️ **Everyday assistance**\n\n"
        "Just send me a message or prompt to get started!"
    )
    await update.message.reply_text(welcome_text, parse_mode="Markdown")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processes user text through OpenAI's API."""
    user_input = update.message.text
    
    # Indicate typing state while processing
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Fast and cost-effective model
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
    if not TELEGRAM_BOT_TOKEN or not OPENAI_API_KEY:
        raise ValueError("Missing TELEGRAM_BOT_TOKEN or OPENAI_API_KEY environment variables.")

    # Build and start telegram bot
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot is up and running...")
    app.run_polling(drop_pending_updates=True)
