
import argparse
import csv
import os

from datetime import datetime
from decimal import Decimal
from pathlib import Path

from cassandra.cluster import Cluster


# ---------------------------------------------------------------------
# CONEXIÓN
# ---------------------------------------------------------------------

def conectar():
    """
    Establece a conexión co clúster Cassandra.
    """
    host = os.getenv("CASSANDRA_HOST", "127.0.0.1")
    port = int(os.getenv("CASSANDRA_PORT", "9042"))

    cluster = Cluster([host], port=port)
    sesion = cluster.connect("parque_eolico")

    return cluster, sesion


# ---------------------------------------------------------------------
# LECTURA E CONVERSIÓN DO CSV
# ---------------------------------------------------------------------

def converter_lectura(fila):
    """
    Converte os tipos de datos dunha fila do CSV
    aos tipos compatibles coas táboas Cassandra.
    """

    data_hora = datetime.strptime(
        fila["data_hora"],
        "%Y-%m-%d %H:%M:%S"
    )

    return {
        "aerogenerador_id": fila["aerogenerador_id"],
        "dia": data_hora.date(),
        "data_hora": data_hora,
        "vento_ms": Decimal(fila["vento_ms"]),
        "direccion_graos": int(fila["direccion_graos"]),
        "potencia_kw": Decimal(fila["potencia_kw"]),
        "rotor_rpm": Decimal(fila["rotor_rpm"]),
        "temp_xerador_c": Decimal(fila["temp_xerador_c"]),
        "estado": fila["estado"]
    }


def ler_csv(ruta_csv):
    """
    Le o CSV e devolve as lecturas convertidas.
    """
    lecturas = []

    with open(ruta_csv, "r", newline="", encoding="utf-8") as ficheiro:

        lector = csv.DictReader(ficheiro)

        for numero, fila in enumerate(lector, start=2):

            try:
                lectura = converter_lectura(fila)
                lecturas.append(lectura)

            except (ValueError, KeyError) as erro:
                raise ValueError(
                    f"Erro na fila {numero} do CSV: {erro}"
                ) from erro

    return lecturas


# ---------------------------------------------------------------------
# INSERCIÓN DAS LECTURAS
# ---------------------------------------------------------------------

def inserir_lectura(sesion, consulta, lectura):
    """
    Insire unha lectura na táboa principal.
    """

    sesion.execute(consulta, (
        lectura["aerogenerador_id"],
        lectura["dia"],
        lectura["data_hora"],
        lectura["vento_ms"],
        lectura["direccion_graos"],
        lectura["potencia_kw"],
        lectura["rotor_rpm"],
        lectura["temp_xerador_c"],
        lectura["estado"]
    ))


# ---------------------------------------------------------------------
# INSERCIÓN DA POTENCIA PARA O CÁLCULO DA ENERXÍA
# ---------------------------------------------------------------------

def inserir_enerxia(sesion, consulta, lectura):
    """
    Garda a potencia de cada intervalo na táboa de enerxía.
    """

    sesion.execute(consulta, (
        lectura["aerogenerador_id"],
        lectura["dia"],
        lectura["data_hora"],
        lectura["potencia_kw"]
    ))


# ---------------------------------------------------------------------
# INSERCIÓN DAS ALARMAS
# ---------------------------------------------------------------------

def inserir_alarma(sesion, consulta, lectura):
    """
    Insire unha lectura unicamente se o seu estado é alarma.
    """

    if lectura["estado"] != "alarma":
        return False

    sesion.execute(consulta, (
        lectura["dia"],
        lectura["data_hora"],
        lectura["aerogenerador_id"],
        lectura["vento_ms"],
        lectura["direccion_graos"],
        lectura["potencia_kw"],
        lectura["rotor_rpm"],
        lectura["temp_xerador_c"],
        lectura["estado"]
    ))

    return True


# ---------------------------------------------------------------------
# ACTUALIZACIÓN DA ÚLTIMA LECTURA
# ---------------------------------------------------------------------

def actualizar_ultima_lectura(sesion, consulta_insert,
                               consulta_update, lectura):
    """
    Actualiza a última lectura dun aeroxerador.

    Evita sobrescribir unha lectura máis recente
    cunha lectura anterior.
    """

    valores = (
        lectura["aerogenerador_id"],
        lectura["data_hora"],
        lectura["vento_ms"],
        lectura["direccion_graos"],
        lectura["potencia_kw"],
        lectura["rotor_rpm"],
        lectura["temp_xerador_c"],
        lectura["estado"]
    )

    # Se o aeroxerador non ten rexistro, créase.
    resultado = sesion.execute(
        consulta_insert,
        valores
    )

    if resultado.one().applied:
        return True

    # Se xa existe, actualízase só se a nova data é posterior.
    resultado = sesion.execute(
        consulta_update,
        (
            lectura["data_hora"],
            lectura["vento_ms"],
            lectura["direccion_graos"],
            lectura["potencia_kw"],
            lectura["rotor_rpm"],
            lectura["temp_xerador_c"],
            lectura["estado"],
            lectura["aerogenerador_id"],
            lectura["data_hora"]
        )
    )

    return resultado.one().applied


# ---------------------------------------------------------------------
# CARGA COMPLETA DOS DATOS
# ---------------------------------------------------------------------

def cargar_datos(ruta_csv):
    """
    Coordina a lectura do CSV e a inserción das lecturas
    nas catro táboas Cassandra.
    """

    lecturas = ler_csv(ruta_csv)

    if not lecturas:
        print("O ficheiro CSV non contén lecturas.")
        return

    cluster, sesion = conectar()

    try:

        # Consultas preparadas para as catro táboas.

        consulta_lecturas = sesion.prepare("""
            INSERT INTO lecturas_aerogenerador_dia (
                aerogenerador_id,
                dia,
                data_hora,
                vento_ms,
                direccion_graos,
                potencia_kw,
                rotor_rpm,
                temp_xerador_c,
                estado
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """)

        consulta_enerxia = sesion.prepare("""
            INSERT INTO energia_aerogenerador_dia (
                aerogenerador_id,
                dia,
                data_hora,
                potencia_kw
            ) VALUES (?, ?, ?, ?)
        """)

        consulta_alarmas = sesion.prepare("""
            INSERT INTO alarmas_dia (
                dia,
                data_hora,
                aerogenerador_id,
                vento_ms,
                direccion_graos,
                potencia_kw,
                rotor_rpm,
                temp_xerador_c,
                estado
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """)

        consulta_ultima_insert = sesion.prepare("""
            INSERT INTO ultima_lectura_aerogenerador (
                aerogenerador_id,
                data_hora,
                vento_ms,
                direccion_graos,
                potencia_kw,
                rotor_rpm,
                temp_xerador_c,
                estado
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            IF NOT EXISTS
        """)

        consulta_ultima_update = sesion.prepare("""
            UPDATE ultima_lectura_aerogenerador
            SET data_hora = ?,
                vento_ms = ?,
                direccion_graos = ?,
                potencia_kw = ?,
                rotor_rpm = ?,
                temp_xerador_c = ?,
                estado = ?
            WHERE aerogenerador_id = ?
            IF data_hora < ?
        """)

        # Contadores.
        total_lecturas = 0
        total_alarmas = 0
        total_ultimas = 0

        # Gardamos a lectura máis recente de cada aeroxerador
        # para actualizar a cuarta táboa unha soa vez por máquina.

        ultimas_lecturas = {}

        for lectura in lecturas:

            inserir_lectura(
                sesion,
                consulta_lecturas,
                lectura
            )

            inserir_enerxia(
                sesion,
                consulta_enerxia,
                lectura
            )

            if inserir_alarma(
                sesion,
                consulta_alarmas,
                lectura
            ):
                total_alarmas += 1

            aeroxerador_id = lectura["aerogenerador_id"]

            anterior = ultimas_lecturas.get(aeroxerador_id)

            if (
                anterior is None
                or lectura["data_hora"] > anterior["data_hora"]
            ):
                ultimas_lecturas[aeroxerador_id] = lectura

            total_lecturas += 1

        # Actualización da última lectura de cada aeroxerador.

        for lectura in ultimas_lecturas.values():

            if actualizar_ultima_lectura(
                sesion,
                consulta_ultima_insert,
                consulta_ultima_update,
                lectura
            ):
                total_ultimas += 1

        print("\n--- RESUMO DA CARGA ---")
        print(f"Lecturas procesadas: {total_lecturas}")
        print(f"Alarmas inseridas: {total_alarmas}")
        print(f"Aeroxeradores actualizados: {total_ultimas}")
        print("Carga completada correctamente.")

    finally:
        cluster.shutdown()


# ---------------------------------------------------------------------
# EXECUCIÓN
# ---------------------------------------------------------------------

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Carga de lecturas no clúster Cassandra."
    )

    parser.add_argument(
        "csv",
        type=Path,
        help="Ruta do ficheiro CSV coas lecturas."
    )

    args = parser.parse_args()

    if not args.csv.is_file():
        parser.error(f"Non existe o ficheiro: {args.csv}")

    cargar_datos(args.csv)
