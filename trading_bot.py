# Análisis técnico y señales
import os import time import requests import numpy as np import pandas as pd from datetime import datetime from dotenv import load_dotenv from telegram import Bot

Cargar claves del .env

load_dotenv("llamado.env")

BYBIT_API_KEY = os.getenv("BYBIT_API_KEY") BYBIT_SECRET = os.getenv("BYBIT_SECRET") TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN") TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

TIMEFRAMES = ["60", "240", "D"]  # 1h, 4h, 1d SYMBOL = "BTCUSDT"

bot = Bot(token=TELEGRAM_TOKEN)

def get_candles(symbol, interval, limit=100): url = f"https://api.bybit.com/v5/market/kline?category=linear&symbol={symbol}&interval={interval}&limit={limit}" response = requests.get(url) data = response.json() if data['retCode'] != 0: print("Error al obtener velas:", data['retMsg']) return None df = pd.DataFrame(data['result']['list'], columns=[ 'timestamp', 'open', 'high', 'low', 'close', 'volume', 'turnover' ]) df['close'] = df['close'].astype(float) df['high'] = df['high'].astype(float) df['low'] = df['low'].astype(float) df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms') return df

def calculate_indicators(df): df['EMA9'] = df['close'].ewm(span=9).mean() df['EMA21'] = df['close'].ewm(span=21).mean() delta = df['close'].diff() gain = delta.where(delta > 0, 0) loss = -delta.where(delta < 0, 0) avg_gain = gain.rolling(window=14).mean() avg_loss = loss.rolling(window=14).mean() rs = avg_gain / avg_loss df['RSI'] = 100 - (100 / (1 + rs)) return df

def detect_support_resistance(df): support = df['low'].rolling(window=5).min().iloc[-1] resistance = df['high'].rolling(window=5).max().iloc[-1] return support, resistance

def detect_signal(df): last = df.iloc[-1] prev = df.iloc[-2] support, resistance = detect_support_resistance(df)

# Condiciones de compra
if prev['EMA9'] < prev['EMA21'] and last['EMA9'] > last['EMA21'] and last['RSI'] < 70 and last['close'] > support:
    return 'BUY', last['close'], support, resistance
# Condiciones de venta
elif prev['EMA9'] > prev['EMA21'] and last['EMA9'] < last['EMA21'] and last['RSI'] > 30 and last['close'] < resistance:
    return 'SELL', last['close'], support, resistance
return None, None, None, None

def send_alert(signal, price, support, resistance, tf): tp1 = price * 1.02 if signal == 'BUY' else price * 0.98 tp2 = price * 1.04 if signal == 'BUY' else price * 0.96 sl = price * 0.98 if signal == 'BUY' else price * 1.02

message = f"\n📢 Señal de {signal}\n🕒 Timeframe: {tf}\n📉 Precio actual: ${price:.2f}\n⚙️ EMA9 {'>' if signal=='BUY' else '<'} EMA21\n📊 RSI: integrado\n🔹 {'Soporte' if signal=='BUY' else 'Resistencia'} detectado en: ${support:.2f if support else 0}\n🎯 TP1: ${tp1:.2f} | TP2: ${tp2:.2f}\n🛑 SL: ${sl:.2f}"
bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)

def run(): for tf in TIMEFRAMES: df = get_candles(SYMBOL, tf) if df is None: continue df = calculate_indicators(df) signal, price, support, resistance = detect_signal(df) if signal: send_alert(signal, price, support, resistance, tf)

if name == 'main': while True: run() time.sleep(300)  # cada 5 minutos


