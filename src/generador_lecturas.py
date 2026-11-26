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

# vento
VENTO_ARRANQUE = 3.0
VENTO_NOMINAL = 12.0
VENTO_MAX_FUNCIONAMENTO = 25.0

# Función para cumplir la regla 2 "potencia segundo o vento"
#Calcula qué parte del intervalo entre 3 y 12 m/s hemos recorrido.
#Multiplica esa proporción por los 3.000 kW máximos.
# vento_ms - VENTO_ARRANQUE: calcula cuánto viento tenemos por encima del mínimo necesario para arrancar.
# VENTO_NOMINAL - VENTO_ARRANQUE: calcula cuánto viento necesitamos para pasar del arranque a la potencia máxima.

def calcula_potencia(vento_ms):
    """Calcula a potencia en función da velocidade do vento."""
    #Si el viento es menor a 3ms o mayor a 25ms = 0 de potencia
    if vento_ms < VENTO_ARRANQUE or vento_ms > VENTO_MAX_FUNCIONAMENTO:
        potencia = POTENCIA_MIN
    #entre 3 y 12 se calcula el aumento ya que (potencia sobe co vento)
    elif vento_ms < VENTO_NOMINAL:
        proporcion = (vento_ms - VENTO_ARRANQUE) / (VENTO_NOMINAL - VENTO_ARRANQUE)
        potencia = proporcion * POTENCIA_MAX
    #entre 12 y 25 = 3000kw
    else:
        potencia = POTENCIA_MAX

    return round(potencia, 1)

#Función para generar una lectura por aeroxerador y día
#Generamos una probabilidad del 1% en qeu salgan temps altas para poder realizar un estado de alarma
#Generamos un vento_ms por random.uniform para poder calcular la potencia y realizar un estado de parado(si es 0)
#si el estado es parado -> rpm a 0
#Generamos direcciones
def lectura(aeroxerador_id, data_hora):

    """Xera unha lectura que cumpre o contrato."""

    #sin variación
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

    # Calculamos la potencia
    potencia_kw = calcula_potencia(vento_ms)

    # Calculamos las revoluciones
    if estado == ESTADO_PARADO:
        rotor_rpm = ROTOR_MIN
    else:
        rotor_rpm = round(random.uniform(ROTOR_MIN, ROTOR_MAX), 1)

    # Resto de valores
    direccion_graos = random.randint(GRAO_MIN, GRAO_MAX)

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

#Utilizamos la función xera_lecturas para poder devolver una lista de estas según los dias marcados 
#Generamos espacios de 10 minutos entre cada generación de grupo de lecturas por aeroxeradores
def xera_lecturas(dias):
    """Xera as lecturas de todos os aeroxeradores."""

    lecturas = []

    for dia in range(dias):
        for intervalo in range(LECTURAS_POR_DIA):

            data_hora = PRIMEIRO_DIA + timedelta(
                days=dia,
                minutes=intervalo * MINUTOS
            )

            for aeroxerador_id in AEROGENERADORES:

                nova_lectura = lectura(
                    aeroxerador_id,
                    data_hora
                )

                lecturas.append(nova_lectura)

    return lecturas


#Comprobamos que cumplen las reglas de contrato por cada una de las lecturas
def cumpre_contrato(lectura):
    """Comproba que unha lectura cumpre o contrato."""

    # Comprobamos o identificador do aeroxerador
    if lectura["aerogenerador_id"] not in AEROGENERADORES:
        return False

    # Comprobamos os rangos dos valores
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

    # Comprobamos que o estado sexa válido
    if lectura["estado"] not in (ESTADO_OK, ESTADO_ALARMA, ESTADO_PARADO):
        return False

    vento = lectura["vento_ms"]
    potencia = lectura["potencia_kw"]
    rotor = lectura["rotor_rpm"]
    temperatura = lectura["temp_xerador_c"]
    estado = lectura["estado"]

    # A potencia debe corresponderse coa velocidade do vento
    if potencia != calcula_potencia(vento):
        return False

    # Comprobamos o estado parado
    if estado == ESTADO_PARADO:
        if vento >= VENTO_ARRANQUE and vento <= VENTO_MAX_FUNCIONAMENTO:
            return False

        if potencia != POTENCIA_MIN or rotor != ROTOR_MIN:
            return False

    # Comprobamos o estado de alarma
    elif estado == ESTADO_ALARMA:
        if vento < VENTO_ARRANQUE or vento > VENTO_MAX_FUNCIONAMENTO:
            return False

        if temperatura < TEMP_ALARMA:
            return False

    # Comprobamos o estado normal
    elif estado == ESTADO_OK:
        if vento < VENTO_ARRANQUE or vento > VENTO_MAX_FUNCIONAMENTO:
            return False

        if temperatura >= TEMP_ALARMA:
            return False

    return True

#Para poder generar el csv , utilizamos main pasandole argumentos 
#cuantos días que queremos generar , semente , nombre del archivo
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