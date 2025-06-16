import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from trading_bot import get_signal
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Bot iniciado.")

async def signal_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sig = get_signal()
    await update.message.reply_text(sig or "No hay señal de trading ahora.")

def run():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("signal", signal_cmd))
    print("Bot corriendo...")
    app.run_polling()
