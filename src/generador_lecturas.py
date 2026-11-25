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
TEMP_ALARMA = 80.0

# vento -> cambia pouco dunha lectura á seguinte e distintos aeroxeradores teñen ventos parecidos á mesma hora
CAMBIO_MAX_VENTO = 0.5
vento_anterior_primera_lectura = random.uniform(VENTO_MIN, VENTO_MAX)
VENTO_ARRANQUE = 3.0
VENTO_NOMINAL = 12.0
VENTO_MAX_FUNCIONAMENTO = 25.0

def xera_vento_anterior(vento_anterior):
    """Xera o vento de referencia do parque."""
    cambio = random.uniform(-CAMBIO_MAX_VENTO, CAMBIO_MAX_VENTO) #genera una variación aleatoria entre -0,5 y +0,5 (puede ser -0,2 o +0,3 por ejemplo)

    vento = vento_anterior + cambio #calcula el nuevo viento a partir del anterior. Le suma al viento anterior el cambio (puede restar o sumar al valor)

    vento = max(VENTO_MIN, min(VENTO_MAX, vento)) #evitan que el viento salga del rango permitido, de 0 a 30 m/s.

    return round(vento, 1)

def calcula_potencia(vento_ms):
    """Calcula a potencia en función da velocidade do vento."""

    if vento_ms < VENTO_ARRANQUE or vento_ms > VENTO_MAX_FUNCIONAMENTO:
        potencia = POTENCIA_MIN

    elif vento_ms < VENTO_NOMINAL:
        proporcion = (vento_ms - VENTO_ARRANQUE) / (VENTO_NOMINAL - VENTO_ARRANQUE)
        potencia = proporcion * POTENCIA_MAX

    else:
        potencia = POTENCIA_MAX

    return round(potencia, 1)


def lectura(aeroxerador_id, data_hora, vento_primera):
    """Xera unha lectura que cumpre o contrato."""

    # Vento particular do aeroxerador
    # variacion = random.uniform(-0.3, 0.3)
    # vento_ms = round(vento_primera + variacion, 1)

    # # Evitamos salir del rango permitido
    # vento_ms = max(VENTO_MIN, min(VENTO_MAX, vento_ms))
    # Xeración independente do vento para probar as paradas

    #pruebas sin variación
    vento_ms = round(random.uniform(VENTO_MIN, VENTO_MAX), 1)
     
    # Xeración da temperatura e da posible alarma
    if random.random() < PROBABILIDADE_ALARMA:
        temp_xerador_c = round(
            random.uniform(TEMP_ALARMA, TEMP_XERADOR_MAX), 1
        )
        ten_alarma = True

    else:
        temp_xerador_c = round(
            random.uniform(TEMP_XERADOR_MIN, TEMP_ALARMA - 0.1), 1
        )
        ten_alarma = False

    # Determinación do estado
    if vento_ms < VENTO_ARRANQUE or vento_ms > VENTO_MAX_FUNCIONAMENTO:
        estado = ESTADO_PARADO

    elif ten_alarma:
        estado = ESTADO_ALARMA

    else:
        estado = ESTADO_OK


    # # Determinamos el estado
    # if vento_ms < VENTO_ARRANQUE or vento_ms > VENTO_MAX_FUNCIONAMENTO:
    #     estado = ESTADO_PARADO

    # elif random.random() < PROBABILIDADE_ALARMA:
    #     estado = ESTADO_ALARMA

    # else:
    #     estado = ESTADO_OK



    # Calculamos la potencia
    potencia_kw = calcula_potencia(vento_ms)

    # Calculamos las revoluciones
    if estado == ESTADO_PARADO:
        rotor_rpm = ROTOR_MIN
    else:
        rotor_rpm = round(random.uniform(ROTOR_MIN, ROTOR_MAX), 1)

    # Resto de valores
    direccion_graos = random.randint(GRAO_MIN, GRAO_MAX)
    # temp_xerador_c = round(random.uniform(TEMP_XERADOR_MIN, TEMP_XERADOR_MAX), 1)

    return {
        "aerogenerador_id": aeroxerador_id,
        "data_hora": data_hora.strftime("%Y-%m-%d %H:%M:%S"),
        "vento_ms": vento_ms,
        "direccion_graos": direccion_graos,
        "potencia_kw": potencia_kw,
        "rotor_rpm": rotor_rpm,
        "temp_xerador_c": temp_xerador_c,
        "estado": estado
    }


def xera_lecturas(dias):
    """Xera as lecturas de todos os aeroxeradores."""

    lecturas = []
    vento_anterior = random.uniform(VENTO_MIN, VENTO_MAX)

    for dia in range(dias):
        for intervalo in range(LECTURAS_POR_DIA):

            data_hora = PRIMEIRO_DIA + timedelta(
                days=dia,
                minutes=intervalo * MINUTOS
            )

            vento_referencia = xera_vento_anterior(vento_anterior)
            vento_anterior = vento_referencia

            for aeroxerador_id in AEROGENERADORES:

                nova_lectura = lectura(
                    aeroxerador_id,
                    data_hora,
                    vento_referencia
                )

                lecturas.append(nova_lectura)

    return lecturas


def cumpre_contrato(lectura):
    """Comproba que unha lectura cumpre o contrato."""

    if lectura["aerogenerador_id"] not in AEROGENERADORES:
        return False

    if not VENTO_MIN <= lectura["vento_ms"] <= VENTO_MAX:
        return False

    if not GRAO_MIN <= lectura["direccion_graos"] <= GRAO_MAX:
        return False

    if not POTENCIA_MIN <= lectura["potencia_kw"] <= POTENCIA_MAX:
        return False

    if not ROTOR_MIN <= lectura["rotor_rpm"] <= ROTOR_MAX:
        return False

    if not TEMP_XERADOR_MIN <= lectura["temp_xerador_c"] <= TEMP_XERADOR_MAX:
        return False

    if lectura["estado"] not in (ESTADO_OK, ESTADO_ALARMA, ESTADO_PARADO):
        return False

    if lectura["estado"] == ESTADO_PARADO:
        if lectura["potencia_kw"] != 0 or lectura["rotor_rpm"] != 0:
            return False

    if lectura["potencia_kw"] != calcula_potencia(lectura["vento_ms"]):
        return False

    return True


if __name__ == "__main__":

    # Argumentos
    parser = argparse.ArgumentParser(
        description="Xerador de lecturas dun parque eólico."
    )

    parser.add_argument("--dias", type=int, default=1,
                        help="Número de días que se van xerar.")

    parser.add_argument("--semente", type=int, default=42,
                        help="Semente para reproducir a xeración.")

    parser.add_argument("--saida", type=str, default="lecturas.csv",
                        help="Nome do ficheiro CSV de saída.")

    args = parser.parse_args()

    if args.dias <= 0:
        parser.error("--dias debe ser maior que cero.")

    # Semente
    random.seed(args.semente)

    # Xeración das lecturas
    lecturas = xera_lecturas(args.dias)

    # Validación
    if not all(cumpre_contrato(l) for l in lecturas):
        raise ValueError("Hai lecturas que non cumpren o contrato.")

    # Xeración do CSV
    with open(args.saida, "w", newline="", encoding="utf-8") as ficheiro:

        campos = [
            "aerogenerador_id",
            "data_hora",
            "vento_ms",
            "direccion_graos",
            "potencia_kw",
            "rotor_rpm",
            "temp_xerador_c",
            "estado"
        ]

        escritor = csv.DictWriter(ficheiro, fieldnames=campos)
        escritor.writeheader()
        escritor.writerows(lecturas)

    print(f"Lecturas xeradas: {len(lecturas)}")
    print(f"Ficheiro CSV: {args.saida}")