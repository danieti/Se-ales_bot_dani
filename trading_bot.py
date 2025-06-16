import os
import requests
import pandas as pd
import numpy as np
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

BYBIT_API_KEY = os.getenv("BYBIT_API_KEY")
BYBIT_SECRET = os.getenv("BYBIT_SECRET")

def obtener_velas(simbolo, intervalo, limite=100):
    url = f"https://api.bybit.com/v5/market/kline?category=linear&symbol={simbolo}&interval={intervalo}&limit={limite}"
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
    df['EMA_20'] = df['close'].ewm(span=20).mean()
    df['EMA_50'] = df['close'].ewm(span=50).mean()

    delta = df['close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()
    rs = avg_gain / avg_loss
    df['RSI'] = 100 - (100 / (1 + rs))

    df['MACD'] = df['close'].ewm(span=12).mean() - df['close'].ewm(span=26).mean()
    df['Signal'] = df['MACD'].ewm(span=9).mean()

    return df

def detectar_entrada(df):
    ultima = df.iloc[-1]

    # Condiciones simples de entrada
    cruce_ema = ultima['EMA_20'] > ultima['EMA_50']
    rsi_ok = ultima['RSI'] < 30 or ultima['RSI'] > 70
    macd_ok = ultima['MACD'] > ultima['Signal']

    if cruce_ema and rsi_ok and macd_ok:
        sl = round(ultima['close'] * 0.98, 2)
        tp1 = round(ultima['close'] * 1.03, 2)
        tp2 = round(ultima['close'] * 1.06, 2)

        return f"Entrada detectada ⚡\nPrecio: {ultima['close']}\nSL: {sl}\nTP1: {tp1}\nTP2: {tp2}\nRSI: {round(ultima['RSI'],2)}"
    else:
        return None

def obtener_senal(simbolo, timeframe):
    df = obtener_velas(simbolo, timeframe)
    if df is None or len(df) < 50:
        return None

    df = calcular_indicadores(df)
    return detectar_entrada(df)