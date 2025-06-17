import os
import requests
import numpy as np
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def obtener_velas(simbolo, intervalo, limite=100):
    url = f"https://api.bybit.com/v5/market/kline?category=linear&symbol={simbolo}&interval={intervalo}&limit={limite}"
    response = requests.get(url)
    data = response.json()

    if data['retCode'] != 0:
        print("Error al obtener velas:", data['retMsg'])
        return None

    df = pd.DataFrame(data['result']['list'], columns=[
        'timestamp', 'open', 'high', 'low', 'close', 'volume', 'turnover'
    ])
    df[['open', 'high', 'low', 'close']] = df[['open', 'high', 'low', 'close']].astype(float)
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df

def analizar_estrategia(df):
    df['ema_20'] = df['close'].ewm(span=20).mean()
    df['ema_50'] = df['close'].ewm(span=50).mean()
    df['rsi'] = calcular_rsi(df['close'], 14)
    df['macd'], df['macd_signal'] = calcular_macd(df['close'])

    ultima = df.iloc[-1]
    entrada = None

    if ultima['ema_20'] > ultima['ema_50'] and ultima['macd'] > ultima['macd_signal'] and ultima['rsi'] > 50:
        entrada = 'LONG'
    elif ultima['ema_20'] < ultima['ema_50'] and ultima['macd'] < ultima['macd_signal'] and ultima['rsi'] < 50:
        entrada = 'SHORT'

    return entrada, ultima

def calcular_rsi(series, periodo=14):
    delta = series.diff()
    ganancia = delta.where(delta > 0, 0)
    perdida = -delta.where(delta < 0, 0)
    media_ganancia = ganancia.rolling(window=periodo).mean()
    media_perdida = perdida.rolling(window=periodo).mean()
    rs = media_ganancia / media_perdida
    return 100 - (100 / (1 + rs))

def calcular_macd(series):
    ema12 = series.ewm(span=12).mean()
    ema26 = series.ewm(span=26).mean()
    macd = ema12 - ema26
    signal = macd.ewm(span=9).mean()
    return macd, signal

def calcular_sl_tp(precio_entrada, direccion):
    if direccion == 'LONG':
        sl = precio_entrada * 0.98
        tp1 = precio_entrada + (precio_entrada - sl)
        tp2 = precio_entrada + 2 * (precio_entrada - sl)
    elif direccion == 'SHORT':
        sl = precio_entrada * 1.02
        tp1 = precio_entrada - (sl - precio_entrada)
        tp2 = precio_entrada - 2 * (sl - precio_entrada)
    else:
        sl = tp1 = tp2 = None

    return round(sl, 2), round(tp1, 2), round(tp2, 2)

def obtener_senal(simbolo, intervalo):
    df = obtener_velas(simbolo, intervalo)
    if df is None or df.empty:
        return "❌ No se pudieron obtener velas."

    senal, ultima = analizar_estrategia(df)

    if senal:
        sl, tp1, tp2 = calcular_sl_tp(ultima['close'], senal)
        return f"✅ Señal {senal} detectada\n💰 Entrada: {ultima['close']}\n🛑 SL: {sl}\n🎯 TP1: {tp1}\n🎯 TP2: {tp2}"
    else:
        return "📉 Sin señal en esta vela."