CREATE KEYSPACE IF NOT EXISTS cs5424
WITH replication = {
    'class': 'SimpleStrategy',
    'replication_factor': 3
};

USE cs5424;

COPY related_customers [(C_ID, C_W_ID, C_D_ID, R_ID, R_W_ID, R_D_ID)]
FROM '~/cs5424-distributed-database-group-project/cassandra/project-files/preprocessed-data-files/related_customers.csv'
WITH DELIMITER=',' AND HEADER=FALSE;

COPY item_orders [(W_ID, I_ID, O_ID, D_ID, C_ID)]
FROM '~/cs5424-distributed-database-group-project/cassandra/project-files/preprocessed-data-files/item_orders.csv'
WITH DELIMITER=',' AND HEADER=FALSE;
