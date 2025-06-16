import os
import time
from telegram import Bot
from trading_bot import obtener_senal
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

bot = Bot(token=TELEGRAM_TOKEN)

def enviar_mensaje(texto):
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=texto)

def iniciar_bot():
    while True:
        for timeframe in ['1h', '4h', '1d']:
            senal = obtener_senal('BTCUSDT', timeframe)
            if senal:
                mensaje = f"📈 Señal detectada en {timeframe}:\n{senal}"
            else:
                mensaje = f"⏳ Sin señal en {timeframe}."

            enviar_mensaje(mensaje)
            time.sleep(1)  # Pequeño delay para evitar spam

        time.sleep(60)  # Esperar 1 minuto antes de la próxima ronda