# Issue 1 – Configuración do clúster Cassandra

## 1. Obxectivo

Configurar un clúster Cassandra 4.1 con tres nodos e un servizo Python, utilizando Docker Compose.

## 2. Configuración do clúster

O clúster está formado por tres nodos:

- `cassandra1`
- `cassandra2`
- `cassandra3`

Os tres pertencen ao clúster `ParqueEolicoCluster` e ao centro de datos `datacenter1`.

A comprobación con `nodetool status` permite verificar que os tres nodos están activos (`UN`).

![Estado dos tres nodos Cassandra](img/issue1_cap1.png)

## 3. Creación do keyspace

Creouse o keyspace `parque_eolico` mediante o ficheiro `cql/schema.cql`, utilizando:

- Estratexia de replicación: `NetworkTopologyStrategy`.
- Factor de replicación: `3`.
- Centro de datos: `datacenter1`.

A configuración comprobouse mediante `DESCRIBE KEYSPACE parque_eolico`.

![Configuración do keyspace](img/issue1_cap3.png)

## 4. Proba de datos

Mediante o ficheiro `cql/test_persistence.cql` creouse a táboa `test_persistencia` e inseriuse un rexistro de proba.

A consulta `SELECT` confirmou que o dato foi almacenado e recuperado correctamente.

![Resultado da consulta de datos](img/issue1_cap2.png)

## 5. Contedores Docker

Comprobouse que os servizos do proxecto están en execución mediante `docker compose ps`.

![Estado dos contedores Docker](img/issue1_cap4.png)

## 6. Conclusión

A configuración permite executar un clúster Cassandra de tres nodos, cun keyspace replicado nos tres nodos e unha táboa na que se poden inserir e consultar datos.