CREATE KEYSPACE IF NOT EXISTS cs5424
WITH replication = {
    'class': 'SimpleStrategy',
    'replication_factor': 3
};

USE cs5424;

DROP TABLE item;
CREATE TABLE item (
    I_ID    int PRIMARY KEY,
    I_NAME  varchar,
    I_PRICE decimal,
    I_IM_ID int,
    I_DATA  varchar
);
COPY item (I_ID, I_NAME, I_PRICE, I_IM_ID, I_DATA)
FROM '~/cs5424-distributed-database-group-project/cassandra/project-files/data-files/item.csv'
WITH DELIMITER=',' AND HEADER=FALSE;