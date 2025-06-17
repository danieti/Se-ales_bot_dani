# Aquí puedes meter funciones generales (por ejemplo convertir UTC, logs, etc.)
from datetime import datetime

def ms_a_fecha(ms):
    """Convierte milisegundos a formato de fecha legible."""
    return datetime.fromtimestamp(int(ms) / 1000).strftime('%Y-%m-%d %H:%M:%S')

def calcular_niveles_fibonacci(entrada, sl, ratio=2):
    """
    Calcula TP1 y TP2 usando una proporción riesgo:beneficio.
    TP1 = entrada + distancia * 1
    TP2 = entrada + distancia * ratio
    """
    riesgo = abs(entrada - sl)
    tp1 = entrada + riesgo
    tp2 = entrada + (riesgo * ratio)
    return round(tp1, 2), round(tp2, 2)

def formatear_mensaje(senal, marco):
    """
    Formatea el mensaje de alerta para Telegram.
    """
    if senal['tipo'] == 'compra' or senal['tipo'] == 'venta':
        return f"""
📊 Señal detectada ({marco})
Tipo: {senal['tipo'].upper()}
Entrada: {senal['entrada']}
Stop Loss: {senal['sl']}
Take Profit 1: {senal['tp1']}
Take Profit 2: {senal['tp2']}
RSI: {senal['rsi']}
MACD: {senal['macd']}
"""
    else:
        return f"⏳ [{marco}] Sin señal clara esta vez. RSI: {senal['rsi']} - MACD: {senal['macd']}"