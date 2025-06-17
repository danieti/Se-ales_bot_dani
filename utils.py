import numpy as np

def calcular_fibonacci(entrada, stop_loss):
    distancia = abs(entrada - stop_loss)
    tp1 = entrada + (distancia * 1.618) if entrada > stop_loss else entrada - (distancia * 1.618)
    tp2 = entrada + (distancia * 2.618) if entrada > stop_loss else entrada - (distancia * 2.618)
    return round(tp1, 2), round(tp2, 2)

def detectar_soporte_resistencia(df):
    # Solo una simplificación para soporte y resistencia básicos
    soporte = df['low'].rolling(window=5).min().iloc[-1]
    resistencia = df['high'].rolling(window=5).max().iloc[-1]
    return round(soporte, 2), round(resistencia, 2)

def formatear_mensaje(entrada, sl, tp1, tp2, simbolo, tf):
    return (
        f"📊 Señal detectada para {simbolo} en {tf}\n\n"
        f"🟢 Entrada: {entrada}\n"
        f"🔴 Stop Loss: {sl}\n"
        f"🎯 Take Profit 1: {tp1}\n"
        f"🎯 Take Profit 2: {tp2}"
    )