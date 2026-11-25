-- CQL de esquema base de las tablas 
-- En este cql se procederá a generar las tablas para guardar las lecturas
-- docker compose exec cassX cqlsh -f /cql/esquema_tablas.cql

CREATE KEYSPACE IF NOT EXISTS parque_eolico
  WITH replication = {'class': 'NetworkTopologyStrategy', 'dc1': 3};

USE parque_eolico;

-- Consulta: "As lecturas dun aeroxerador nun día, das máis recentes ás máis antigas."
-- Notas : Como data_hora va aumentando su valor cada 10 min , las más recientes serán las últimas
-- aerogenerador_id TEXT : MB del 1 al 12

CREATE TABLE lecturas_aerogenerador_dia (
    aerogenerador_id TEXT,
    dia DATE,
    data_hora TIMESTAMP,
    vento_ms DECIMAL,
    direccion_graos INT,
    potencia_kw DECIMAL,
    rotor_rpm DECIMAL,
    temp_xerador_c DECIMAL,
    estado TEXT,
    PRIMARY KEY ((aerogenerador_id, dia), data_hora)
) WITH CLUSTERING ORDER BY (data_hora DESC);


-- Consulta: "A enerxía producida por un aeroxerador nun día (suma da potencia × 10 minutos)"
-- Notas : Guardar lecturas de potencia y calcular cuando hagamos la consulta.
-- Solo vamos a querer visualizar la potencia , por eso añadimos a la tabla los campos necesarios para que funcione y 
-- No añadimos información poco relevante
-- aerogenerador_id + dia	144 filas por partición ,para que cada consulta no crezca 

CREATE TABLE energia_aerogenerador_dia (
    aerogenerador_id TEXT,
    dia DATE,
    data_hora TIMESTAMP,
    potencia_kw DECIMAL,
    PRIMARY KEY ((aerogenerador_id, dia), data_hora)
);

-- Consulta: "As alarmas dun día en todo o parque, en orde horaria"
-- Alarmas = estado -> ok , alarma (el que guardamos) , parado
-- Al necesitar una consulta de un día entero -> no hacemos particiones por aerogenerador_id si no por dia
-- Añadimos data_hora y aerogenerador_id como claves primarias para ordenenar -> en orde horaria
-- Analizar : aerogenerador_id ASC 

CREATE TABLE alarmas_dia (
    dia DATE,
    data_hora TIMESTAMP,
    aerogenerador_id TEXT,
    vento_ms DECIMAL,
    direccion_graos INT,
    potencia_kw DECIMAL,
    rotor_rpm DECIMAL,
    temp_xerador_c DECIMAL,
    estado TEXT,
    PRIMARY KEY ((dia), data_hora, aerogenerador_id)
) WITH CLUSTERING ORDER BY (data_hora ASC);


-- A última lectura de cada aeroxerador do parque, para o panel de control
-- Cada vez que nuestro script cargue una lectura nueva, también tendrá que actualizar esta tabla.
-- Cada aerogenerador tenga su propia partición
-- Comprobar que la nueva lectura añadida tenga una fecha posterior a la anterior.

CREATE TABLE ultima_lectura_aerogenerador (
    aerogenerador_id TEXT,
    data_hora TIMESTAMP,
    vento_ms DECIMAL,
    direccion_graos INT,
    potencia_kw DECIMAL,
    rotor_rpm DECIMAL,
    temp_xerador_c DECIMAL,
    estado TEXT,
    PRIMARY KEY (aerogenerador_id)
);