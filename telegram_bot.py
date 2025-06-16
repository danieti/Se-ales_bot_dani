import os
import time
from dotenv import load_dotenv
from telegram import Bot
from trading_bot import obtener_senal

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
bot = Bot(token=TELEGRAM_TOKEN)

INTERVALOS = ["60", "240", "D"]  # 1h, 4h, 1D en formato Bybit

def enviar_mensaje(mensaje):
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=mensaje)
    except Exception as e:
        print(f"Error enviando mensaje: {e}")

def iniciar_bot():
    simbolo = "BTCUSDT"  # Puedes cambiar o parametrizar esto

    while True:
        ahora = time.gmtime()
        minuto = ahora.tm_min
        segundo = ahora.tm_sec

        if minuto == 0 and segundo <= 5:
            for intervalo in INTERVALOS:
                mensaje = obtener_senal(simbolo, intervalo)
                enviar_mensaje(f"⏰ [{intervalo}] {mensaje}")
            print("Esperando al siguiente cierre...")
            time.sleep(60)

        time.sleep(1)