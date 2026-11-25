import argparse
import csv
import random
from datetime import datetime, timedelta

# --- O contrato, en datos -----------------------------------------------

AEROGENERADORES = ["MB-01","MB-02","MB-03","MB-04","MB-05","MB-06","MB-07","MB-08","MB-09","MB-10","MB-11","MB-12"]
PRIMEIRO_DIA = datetime(2027, 7, 16)
MINUTOS=10
PROBABILIDADE_ALARMA = 0.01
LECTURAS_POR_DIA = 24 * 60 // MINUTOS

# Rangos
VENTO_MIN=0.0
VENTO_MAX=30.0
GRAO_MIN=0
GRAO_MAX=359
POTENCIA_MIN=0.0
POTENCIA_MAX=3000.0
ROTOR_MIN=0.0
ROTOR_MAX=16.0
TEMP_XERADOR_MIN=10.0
TEMP_XERADOR_MAX=90.0

# Estados
ESTADO_OK = "ok"
ESTADO_ALARMA = "alarma"
ESTADO_PARADO = "parado"

# vento -> cambia pouco dunha lectura á seguinte e distintos aeroxeradores teñen ventos parecidos á mesma hora
CAMBIO_MAX_VENTO = 0.5
vento_anterior_primera_lectura = random.uniform(VENTO_MIN, VENTO_MAX)

def xera_vento_anterior(vento_anterior):
    """Xera o vento de referencia do parque."""
    cambio = random.uniform(-CAMBIO_MAX_VENTO, CAMBIO_MAX_VENTO) #genera una variación aleatoria entre -0,5 y +0,5 (puede ser -0,2 o +0,3 por ejemplo)

    vento = vento_anterior + cambio #calcula el nuevo viento a partir del anterior. Le suma al viento anterior el cambio (puede restar o sumar al valor)

    vento = max(VENTO_MIN, min(VENTO_MAX, vento)) #evitan que el viento salga del rango permitido, de 0 a 30 m/s.

    return round(vento, 1)


def lectura(aeroxerador_id, data_hora, vento_primera):
    """unha lectura que cumpre o contrato."""
    estado = ESTADO_ALARMA if random.random() < PROBABILIDADE_ALARMA else ESTADO_OK
    return {
        "aerogenerador_id": random.choice(AEROGENERADORES),
        # "data_hora": data_hora.strftime("%Y-%m-%d %H:%M:%S"),
        # "barra": random.choice(BARRAS),
        # "pulseira": f"P-{random.randint(1, 5000):04d}",
        # "produto": produto,
        # "unidades": unidades,
        # "importe": f"{CATALOGO[produto] * unidades:.2f}",   # regra: prezo × unidades
    }



def xera_lecturas(dias):
    """Xera as lecturas de todos os aeroxeradores."""
    ...


def cumpre_contrato(lectura):
    """Comproba que unha lectura cumpre o contrato."""
    ...


if __name__ == "__main__":
    # Argumentos
    # Semente
    # Xeración do CSV
    ...