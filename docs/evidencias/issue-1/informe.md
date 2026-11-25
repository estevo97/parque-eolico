# Issue #1 — Configuración do clúster Cassandra con Docker

## 1. Obxectivo

Despregamento dun clúster Cassandra de tres nodos mediante Docker Compose para o proxecto Parque Eólico Monte Brañas.

## 2. Configuración

- **Motor de base de datos:** Apache Cassandra 4.1.
- **Número de nodos:** 3.
- **Nome do clúster:** ParqueEolicoCluster.
- **Centro de datos:** datacenter1.
- **Rede Docker:** parque_eolico_net.
- **Persistencia:** volumes Docker independentes para cada nodo.
- **Servizo adicional:** python-app.

## 3. Configuración do keyspace

Creouse o keyspace `parque_eolico` mediante o ficheiro `cql/schema.cql`.

- Estratexia de replicación: `NetworkTopologyStrategy`.
- Centro de datos: `datacenter1`.
- Factor de replicación: 3.

## 4. Verificacións

### 4.1. Estado do clúster

Comando: `docker compose exec cassandra1 nodetool status`.

Resultado esperado: tres nodos no estado `UN` (Up/Normal).

### 4.2. Creación do keyspace

Comando: `docker compose exec cassandra1 cqlsh -e "DESCRIBE KEYSPACE parque_eolico"`.

Resultado: keyspace creado correctamente con factor de replicación 3.

### 4.3. Proba de persistencia

Pendiente de realizar.

## 5. Evidencias

Engadir capturas dos resultados das comprobacións realizadas.

## 6. Conclusión

O clúster Cassandra de tres nodos foi despregado mediante Docker Compose e o keyspace `parque_eolico` foi creado correctamente. A verificación da persistencia queda pendente.