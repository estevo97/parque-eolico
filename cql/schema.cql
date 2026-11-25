
CREATE KEYSPACE IF NOT EXISTS parque_eolico
WITH replication = {
    'class': 'NetworkTopologyStrategy',
    'datacenter1': 3
};
