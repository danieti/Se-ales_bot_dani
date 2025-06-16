import os
import requests
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

BYBIT_API_KEY = os.getenv("BYBIT_API_KEY")
BYBIT_SECRET = os.getenv("BYBIT_SECRET")
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def get_klines(symbol="BTCUSDT", interval="1h", limit=100):
    url = f"https://api.bybit.com/v5/market/kline?category=linear&symbol={symbol}&interval={interval}&limit={limit}"
    resp = requests.get(url)
    data = resp.json()
    if data["retCode"] != 0:
        return None
    df = pd.DataFrame(data["result"]["list"], columns=['timestamp','open','high','low','close','volume','turnover'])
    df['close'] = df['close'].astype(float)
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df

def get_signal():
    df = get_klines()
    if df is None:
        return None
    last = df['close'].iloc[-2:]
    if last.iloc[-1] > last.iloc[-2]:
        return "🔼 Señal COMPRA"
    return None