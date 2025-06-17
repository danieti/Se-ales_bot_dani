import os
import requests
import pandas as pd
import numpy as np
from datetime import datetime
from dotenv import load_dotenv
from telegram import Bot

from utils import calcular_fibonacci, detectar_soporte_resistencia, formatear_mensaje

load_dotenv()

BYBIT_API = "https://api.bybit.com/v5/market/kline"
BYBIT_SYMBOL = "BTCUSDT"
TIMEFRAMES = {"1h": 60, "4h": 240, "1d": 1440}
LIMIT = 100

bot = Bot(token=os.getenv("TELEGRAM_TOKEN"))
chat_id = os.getenv("TELEGRAM_CHAT_ID")

def obtener_velas(simbolo, tf, limite=LIMIT):
    url = f"{BYBIT_API}?category=linear&symbol={simbolo}&interval={tf}&limit={limite}"
    response = requests.get(url)
    data = response.json()

    if data['retCode'] != 0:
        print("❌ Error al obtener velas:", data['retMsg'])
        return None

    df = pd.DataFrame(data['result']['list'], columns=[
        'timestamp', 'open', 'high', 'low', 'close', 'volume', 'turnover'
    ])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df[['open', 'high', 'low', 'close']] = df[['open', 'high', 'low', 'close']].astype(float)
    return df

def calcular_indicadores(df):
    df['ema20'] = df['close'].ewm(span=20).mean()
    df['ema50'] = df['close'].ewm(span=50).mean()
    df['rsi'] = calcular_rsi(df['close'], 14)
    df['macd'], df['macd_signal'] = calcular_macd(df['close'])
    return df

def calcular_rsi(series, period=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def calcular_macd(series, fast=12, slow=26, signal=9):
    ema_fast = series.ewm(span=fast).mean()
    ema_slow = series.ewm(span=slow).mean()
    macd = ema_fast - ema_slow
    signal_line = macd.ewm(span=signal).mean()
    return macd, signal_line

def detectar_entrada(df):
    # Condición de ejemplo: cruce de EMA + RSI bajo
    if (
        df['ema20'].iloc[-1] > df['ema50'].iloc[-1] and
        df['ema20'].iloc[-2] < df['ema50'].iloc[-2] and
        df['rsi'].iloc[-1] > 50
    ):
        return True
    return False

def analizar_y_enviar(simbolo, tf):
    df = obtener_velas(simbolo, tf)
    if df is None:
        return

    df = calcular_indicadores(df)

    entrada = df['close'].iloc[-1]
    soporte, resistencia = detectar_soporte_resistencia(df)
    sl = soporte if entrada > soporte else resistencia
    tp1, tp2 = calcular_fibonacci(entrada, sl)

    if detectar_entrada(df):
        mensaje = formatear_mensaje(entrada, sl, tp1, tp2, simbolo, tf)
    else:
        mensaje = f"🔍 Sin señal para {simbolo} en temporalidad {tf}."

    bot.send_message(chat_id=chat_id, text=mensaje)