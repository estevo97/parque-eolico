
USE parque_eolico;

CREATE TABLE IF NOT EXISTS test_persistencia (
    id INT PRIMARY KEY,
    descripcion TEXT
);

INSERT INTO test_persistencia (id, descripcion)
VALUES (1, 'Proba de persistencia do cluster Cassandra');

SELECT * FROM test_persistencia;
