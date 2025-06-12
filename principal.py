#principal.py

import os import time import requests import pandas as pd from datetime import datetime from dotenv import load_dotenv from bybit import HTTP

=== Cargar variables de entorno ===

load_dotenv() BYBIT_API_KEY = os.getenv("BYBIT_API_KEY") BYBIT_API_SECRET = os.getenv("BYBIT_API_SECRET") TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

=== Inicializar cliente Bybit ===

session = HTTP(api_key=BYBIT_API_KEY, api_secret=BYBIT_API_SECRET)

=== Config ===

TIMEFRAMES = ["60", "240", "D"]  # 1h, 4h, 1d SYMBOL_LIMIT = 25  # Top 25

=== Telegram ===

def enviar_telegram(mensaje): url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage" payload = { "chat_id": TELEGRAM_CHAT_ID, "text": mensaje, "parse_mode": "Markdown" } try: requests.post(url, data=payload) except Exception as e: print("[ERROR] Telegram:", e)

=== Estrategia (simple con RSI + EMA) ===

def analizar_mercado(symbol, timeframe): try: klines = session.get_kline(symbol=symbol, interval=timeframe, limit=100) datos = pd.DataFrame(klines['result']) datos['close'] = datos['close'].astype(float)

# Calcular indicadores
    datos['EMA20'] = datos['close'].ewm(span=20).mean()
    datos['EMA50'] = datos['close'].ewm(span=50).mean()
    delta = datos['close'].diff()
    ganancia = delta.where(delta > 0, 0)
    perdida = -delta.where(delta < 0, 0)
    avg_gain = ganancia.rolling(window=14).mean()
    avg_loss = perdida.rolling(window=14).mean()
    rs = avg_gain / avg_loss
    datos['RSI'] = 100 - (100 / (1 + rs))

    actual = datos.iloc[-1]

    # Condición de entrada long simple: cruce EMA + RSI
    if actual['EMA20'] > actual['EMA50'] and actual['RSI'] > 50:
        entrada = actual['close']
        sl = entrada * 0.98
        tp1 = entrada * 1.04
        tp2 = entrada * 1.08
        return True, entrada, sl, tp1, tp2
    else:
        return False, None, None, None, None
except Exception as e:
    print(f"[ERROR] Analizando {symbol}:", e)
    return False, None, None, None, None

=== Ciclo principal ===

def main(): while True: try: top = session.get_tickers()["result"][:SYMBOL_LIMIT] symbols = [s['symbol'] for s in top if s['symbol'].endswith("USDT")]

for tf in TIMEFRAMES:
            for symbol in symbols:
                ok, entrada, sl, tp1, tp2 = analizar_mercado(symbol, tf)
                if ok:
                    mensaje = f"\u2705 *Entrada Long Detectada*\n\n*Par:* {symbol}\n*TF:* {tf}\n*Entrada:* {entrada:.2f}\n*SL:* {sl:.2f}\n*TP1:* {tp1:.2f}\n*TP2:* {tp2:.2f}"
                    enviar_telegram(mensaje)
                else:
                    enviar_telegram(f"No hay señal en {symbol} ({tf})")

        # Esperar 1 hora para volver a analizar
        time.sleep(3600)

    except Exception as e:
        enviar_telegram(f"Error general en el bot: {e}")
        time.sleep(60)

if name == "main": main()

