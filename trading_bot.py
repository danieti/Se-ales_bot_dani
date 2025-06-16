import os 
import time 
import requests 
import numpy as np 
import pandas as pd 
from datetime import datetime from dotenv import load_dotenv from telegram import Bot

load_dotenv()

BYBIT_API_KEY = os.getenv("BYBIT_API_KEY") BYBIT_SECRET = os.getenv("BYBIT_SECRET") TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN") TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

bot = Bot(token=TELEGRAM_TOKEN)

def obtener_velas(simbolo, intervalo, limite=100): url = f"https://api.bybit.com/v5/market/kline?category=linear&symbol={simbolo}&interval={intervalo}&limit={limite}" response = requests.get(url) data = response.json()

if data['retCode'] != 0:
    print("Error al obtener velas:", data['retMsg'])
    return None

df = pd.DataFrame(data['result']['list'], columns=[
    'timestamp', 'open', 'high', 'low', 'close', 'volume', 'turnover'
])
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
df[['open', 'high', 'low', 'close']] = df[['open', 'high', 'low', 'close']].astype(float)
return df

def calcular_indicadores(df): df['ema20'] = df['close'].ewm(span=20).mean() df['ema50'] = df['close'].ewm(span=50).mean() df['rsi'] = calcular_rsi(df['close']) df['macd'], df['macd_signal'] = calcular_macd(df['close']) return df

def calcular_rsi(cierres, periodo=14): delta = cierres.diff() ganancia = delta.where(delta > 0, 0) perdida = -delta.where(delta < 0, 0) media_ganancia = ganancia.rolling(periodo).mean() media_perdida = perdida.rolling(periodo).mean() rs = media_ganancia / media_perdida return 100 - (100 / (1 + rs))

def calcular_macd(cierres): exp1 = cierres.ewm(span=12, adjust=False).mean() exp2 = cierres.ewm(span=26, adjust=False).mean() macd = exp1 - exp2 signal = macd.ewm(span=9, adjust=False).mean() return macd, signal

def detectar_entrada(df): ultima = df.iloc[-1] condiciones = [ ultima['ema20'] > ultima['ema50'], ultima['macd'] > ultima['macd_signal'], ultima['rsi'] > 50 ] return all(condiciones)

def calcular_sl_tp(precio_entrada, alto, bajo): riesgo = abs(precio_entrada - bajo) beneficio = riesgo * 2 sl = bajo tp1 = precio_entrada + beneficio * 0.5 tp2 = precio_entrada + beneficio return sl, tp1, tp2

def obtener_senal(simbolo, intervalo): df = obtener_velas(simbolo, intervalo) if df is None or df.empty: return "No se pudo obtener datos."

df = calcular_indicadores(df)

if detectar_entrada(df):
    precio_entrada = df.iloc[-1]['close']
    alto = df.iloc[-1]['high']
    bajo = df.iloc[-1]['low']
    sl, tp1, tp2 = calcular_sl_tp(precio_entrada, alto, bajo)
    return f"✅ Señal de entrada detectada en {simbolo} ({intervalo})\nEntrada: {precio_entrada:.2f}\nSL: {sl:.2f}\nTP1: {tp1:.2f}\nTP2: {tp2:.2f}"
else:
    return f"❌ No hay entrada válida en {simbolo} ({intervalo})"

def enviar_senal(): simbolos = ['BTCUSDT', 'ETHUSDT'] intervalos = ['60', '240', 'D'] for simbolo in simbolos: for intervalo in intervalos: mensaje = obtener_senal(simbolo, intervalo) bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=mensaje)

if name == 'main': while True: enviar_senal() time.sleep(3600)  # Espera 1 hora para volver a verificar

