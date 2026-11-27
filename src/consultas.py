import os
from cassandra.cluster import Cluster
from datetime import date

def conectar():
    host = os.getenv("CASSANDRA_HOST", "127.0.0.1")
    port = int(os.getenv("CASSANDRA_PORT", "9042"))

    cluster = Cluster([host], port=port)
    sesion = cluster.connect("parque_eolico")

    return cluster, sesion

def consultar_lecturas_aeroxerador(sesion, aeroxerador_id, dia):
    """
    Recupera todas as lecturas dun aeroxerador nun día.
    As lecturas devólvense ordenadas cronoloxicamente de máis recentes a máis antigas.
    """
    consulta = """
        SELECT *
        FROM lecturas_aerogenerador_dia
        WHERE aerogenerador_id = %s AND dia = %s
    """

    filas = sesion.execute(consulta, (aeroxerador_id, dia))

    return list(filas)

def calcular_enerxia_diaria(sesion, aeroxerador_id, dia):
    """
    Calcula a enerxía diaria dun aeroxerador a partir das lecturas de potencia.
    Cada lectura representa un intervalo de 10 minutos.
    """
    consulta = """
        SELECT potencia_kw
        FROM energia_aerogenerador_dia
        WHERE aerogenerador_id = %s AND dia = %s
    """

    filas = sesion.execute(consulta, (aeroxerador_id, dia))

    enerxia_total = 0

    for fila in filas:
        enerxia_total += float(fila.potencia_kw) * (10 / 60)

    return enerxia_total

def consultar_alarmas_diarias(sesion, dia):
    """
    Recupera todas as alarmas rexistradas nun día determinado.
    """
    consulta = """
        SELECT *
        FROM alarmas_dia
        WHERE dia = %s
    """

    filas = sesion.execute(consulta, (dia,))

    return list(filas)

def consultar_ultimas_lecturas(sesion):
    """
    Recupera a última lectura almacenada de cada aeroxerador.
    """
    consulta = """
        SELECT *
        FROM ultima_lectura_aerogenerador
    """

    filas = sesion.execute(consulta)

    return list(filas)

def main():
    """
    Executa as consultas e mostra os resultados.
    """
    aeroxerador_id = "MB-01"
    dia = date(2027, 7, 16)

    cluster, sesion = conectar()

    try:
        # 1. Lecturas dun aeroxerador nun día
        print("\n--- LECTURAS DO AEROXERADOR ---")
        lecturas = consultar_lecturas_aeroxerador(
            sesion, aeroxerador_id, dia
        )

        for lectura in lecturas:
            print(
                lectura.data_hora,
                lectura.potencia_kw,
                lectura.estado
            )

        # 2. Enerxía diaria
        print("\n--- ENERXÍA DIARIA ---")
        enerxia = calcular_enerxia_diaria(
            sesion, aeroxerador_id, dia
        )
        print(f"{aeroxerador_id}: {enerxia:.2f} kWh")

        # 3. Alarmas do día
        print("\n--- ALARMAS DIARIAS ---")
        alarmas = consultar_alarmas_diarias(sesion, dia)

        for alarma in alarmas:
            print(
                alarma.data_hora,
                alarma.aerogenerador_id,
                alarma.estado
            )

        # 4. Últimas lecturas de cada aeroxerador
        print("\n--- ÚLTIMAS LECTURAS ---")
        ultimas = consultar_ultimas_lecturas(sesion)

        for lectura in ultimas:
            print(
                lectura.aerogenerador_id,
                lectura.data_hora,
                lectura.potencia_kw,
                lectura.estado
            )

    finally:
        cluster.shutdown()


if __name__ == "__main__":
    main()