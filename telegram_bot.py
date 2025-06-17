import time
from datetime import datetime
from trading_bot import analizar_y_enviar

INTERVALOS = {
    "60": "1h",
    "240": "4h",
    "1440": "1d"
}

# Guarda el timestamp del último cierre procesado por cada tf
ultimo_cierre = {tf: None for tf in INTERVALOS}

def iniciar_bot():
    print("🤖 Bot de señales iniciado...")

    while True:
        ahora = datetime.utcnow()

        for minutos, tf in INTERVALOS.items():
            # Redondear a múltiplo de intervalo
            cierre_actual = int(ahora.timestamp() // (int(minutos) * 60))

            if cierre_actual != ultimo_cierre[tf]:
                print(f"⏰ Analizando {tf} - {ahora.strftime('%Y-%m-%d %H:%M')}")
                try:
                    analizar_y_enviar("BTCUSDT", tf)
                except Exception as e:
                    print(f"⚠️ Error al analizar {tf}: {e}")
                ultimo_cierre[tf] = cierre_actual

        time.sleep(60)