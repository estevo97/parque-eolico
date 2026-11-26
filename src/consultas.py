from cassandra.cluster import Cluster


def conectar():
    """
    Establece a conexión co clúster Cassandra.
    """
    cluster = Cluster(["127.0.0.1"])
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