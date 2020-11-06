CREATE KEYSPACE IF NOT EXISTS cs5424
WITH replication = {
    'class': 'SimpleStrategy',
    'replication_factor': 3
};

USE cs5424;

DROP TABLE IF EXISTS warehouse;
CREATE TABLE warehouse (
    W_ID        int,
    W_NAME      varchar,
    W_STREET_1  varchar,
    W_STREET_2  varchar,
    W_CITY      varchar,
    W_STATE     varchar,
    W_ZIP       varchar,
    W_TAX       decimal,
    W_YTD       decimal,
    PRIMARY KEY (W_ID)
);
COPY warehouse (W_ID, W_NAME, W_STREET_1, W_STREET_2, W_CITY, W_STATE, W_ZIP, W_TAX, W_YTD)
FROM '~/cs5424-distributed-database-group-project/cassandra/project-files/data-files/warehouse.csv'
WITH DELIMITER=',' AND HEADER=FALSE;

DROP TABLE IF EXISTS warehouse_counters;
CREATE TABLE warehouse_counters (
    W_ID            int,
    W_YTD_CHANGE    counter,
    PRIMARY KEY (W_ID)
);

DROP TABLE IF EXISTS district;
CREATE TABLE district (
    D_W_ID      int,
    D_ID        int,
    D_NAME      varchar,
    D_STREET_1  varchar,
    D_STREET_2  varchar,
    D_CITY      varchar,
    D_STATE     varchar,
    D_ZIP       varchar,
    D_TAX       decimal,
    D_YTD       decimal,
    D_O_ID_OFST int,
    PRIMARY KEY (D_W_ID, D_ID)  -- D_W_ID is the partition key
);
COPY district (D_W_ID, D_ID, D_NAME, D_STREET_1, D_STREET_2, D_CITY, D_STATE, D_ZIP, D_TAX, D_YTD, D_O_ID_OFST)
FROM '~/cs5424-distributed-database-group-project/cassandra/project-files/data-files/district.csv'
WITH DELIMITER=',' AND HEADER=FALSE;

DROP TABLE IF EXISTS district_counters;
CREATE TABLE district_counters (
    D_W_ID          int,
    D_ID            int,
    D_YTD_CHANGE    counter,    -- number of cents
    D_O_COUNTER     counter,
    PRIMARY KEY (D_W_ID, D_ID)
);

DROP MATERIALIZED VIEW IF EXISTS customer_balances;     -- cannot drop `customer` table with existing depending materialized views
DROP TABLE IF EXISTS customer;
CREATE TABLE customer (
    C_W_ID          int,
    C_D_ID          int,
    C_ID            int,
    C_FIRST         varchar,
    C_MIDDLE        varchar,
    C_LAST          varchar,
    C_STREET_1      varchar,
    C_STREET_2      varchar,
    C_CITY          varchar,
    C_STATE         varchar,
    C_ZIP           varchar,
    C_PHONE         varchar,
    C_SINCE         timestamp,
    C_CREDIT        varchar,
    C_CREDIT_LIM    decimal,
    C_DISCOUNT      decimal,
    C_BALANCE       decimal,
    C_YTD_PAYMENT   float,
    C_PAYMENT_CNT   int,
    C_DELIVERY_CNT  int,
    C_DATA          varchar,
    PRIMARY KEY ((C_W_ID, C_D_ID), C_ID)  -- C_W_ID and C_D_ID is the partition key
);
COPY customer (C_W_ID, C_D_ID, C_ID, C_FIRST, C_MIDDLE, C_LAST, C_STREET_1, C_STREET_2, C_CITY, C_STATE, C_ZIP,
    C_PHONE, C_SINCE, C_CREDIT, C_CREDIT_LIM, C_DISCOUNT, C_BALANCE, C_YTD_PAYMENT,
    C_PAYMENT_CNT, C_DELIVERY_CNT, C_DATA)
FROM '~/cs5424-distributed-database-group-project/cassandra/project-files/data-files/customer.csv'
WITH DELIMITER=',' AND HEADER=FALSE;

/* Table for the initial values of customer balance.
   Copying all columns to avoid errors, but only C_BALANCE will ever be used,
   and values in this table will never change.
*/
DROP TABLE IF EXISTS customer_initial;
CREATE TABLE customer_initial (
    C_W_ID          int,
    C_D_ID          int,
    C_ID            int,
    C_FIRST         varchar,
    C_MIDDLE        varchar,
    C_LAST          varchar,
    C_STREET_1      varchar,
    C_STREET_2      varchar,
    C_CITY          varchar,
    C_STATE         varchar,
    C_ZIP           varchar,
    C_PHONE         varchar,
    C_SINCE         timestamp,
    C_CREDIT        varchar,
    C_CREDIT_LIM    decimal,
    C_DISCOUNT      decimal,
    C_BALANCE       decimal,
    C_YTD_PAYMENT   float,
    C_PAYMENT_CNT   int,
    C_DELIVERY_CNT  int,
    C_DATA          varchar,
    PRIMARY KEY ((C_W_ID, C_D_ID), C_ID)  -- C_W_ID and C_D_ID is the partition key
);
COPY customer_initial (C_W_ID, C_D_ID, C_ID, C_FIRST, C_MIDDLE, C_LAST, C_STREET_1, C_STREET_2, C_CITY, C_STATE, C_ZIP,
    C_PHONE, C_SINCE, C_CREDIT, C_CREDIT_LIM, C_DISCOUNT, C_BALANCE, C_YTD_PAYMENT,
    C_PAYMENT_CNT, C_DELIVERY_CNT, C_DATA)
FROM '~/cs5424-distributed-database-group-project/cassandra/project-files/data-files/customer.csv'
WITH DELIMITER=',' AND HEADER=FALSE;

DROP MATERIALIZED VIEW IF EXISTS customer_balances;
CREATE MATERIALIZED VIEW customer_balances
AS SELECT C_W_ID, C_D_ID, C_ID, C_FIRST, C_MIDDLE, C_LAST, C_BALANCE
FROM customer
WHERE C_W_ID IS NOT NULL AND C_D_ID IS NOT NULL AND C_ID IS NOT NULL AND C_BALANCE IS NOT NULL
PRIMARY KEY (C_W_ID, C_D_ID, C_ID, C_BALANCE)
WITH CLUSTERING ORDER BY (C_BALANCE DESC);

DROP TABLE IF EXISTS customer_counters;
CREATE TABLE customer_counters (
    C_W_ID                  int,
    C_D_ID                  int,
    C_ID                    int,
    C_BALANCE_CHANGE        counter,    -- number of cents
    C_YTD_PAYMENT_CHANGE    counter,    -- number of cents
    C_PAYMENT_CNT_CHANGE    counter,
    C_DELIVERY_CNT_CHANGE   counter,
    PRIMARY KEY ((C_W_ID, C_D_ID), C_ID)
);

DROP MATERIALIZED VIEW IF EXISTS customer_orders;
DROP TABLE IF EXISTS orders;    -- `order' cannot be used as table's name in Cassandra
CREATE TABLE orders (
    O_W_ID          int,
    O_D_ID          int,
    O_ID            int,
    O_C_ID          int,
    O_CARRIER_ID    varchar,    -- `null' exists at this column in CSV file, use varchar as a workaround
    O_OL_CNT        int,
    O_ALL_LOCAL     int,
    O_ENTRY_D       timestamp,
    PRIMARY KEY ((O_W_ID, O_D_ID), O_ID)  -- O_W_ID and O_D_ID is the partition key
)
WITH CLUSTERING ORDER BY (O_ID DESC);
COPY orders (O_W_ID, O_D_ID, O_ID, O_C_ID, O_CARRIER_ID, O_OL_CNT, O_ALL_LOCAL, O_ENTRY_D)
FROM '~/cs5424-distributed-database-group-project/cassandra/project-files/data-files/order.csv'
WITH DELIMITER=',' AND HEADER=FALSE;

DROP MATERIALIZED VIEW IF EXISTS customer_orders;
CREATE MATERIALIZED VIEW customer_orders
AS SELECT O_W_ID, O_D_ID, O_C_ID, O_ID, O_ENTRY_D, O_CARRIER_ID
FROM orders
WHERE O_W_ID IS NOT NULL AND O_D_ID IS NOT NULL AND O_C_ID IS NOT NULL AND O_ID IS NOT NULL
PRIMARY KEY ((O_W_ID, O_D_ID, O_C_ID), O_ID)
WITH CLUSTERING ORDER BY (O_ID DESC);

DROP TABLE IF EXISTS item;
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

DROP TABLE IF EXISTS order_line;
CREATE TABLE order_line (
    OL_W_ID         int,
    OL_D_ID         int,
    OL_O_ID         int,
    OL_NUMBER       int,
    OL_I_ID         int,
    OL_DELIVERY_D   varchar,    -- `null' exists in CSV
    OL_AMOUNT       decimal,
    OL_SUPPLY_W_ID  int,
    OL_QUANTITY     int,
    OL_DIST_INFO    varchar,
    PRIMARY KEY ((OL_W_ID, OL_D_ID), OL_O_ID, OL_NUMBER)  -- OL_W_ID and OL_D_ID is the partition key
);
COPY order_line (OL_W_ID, OL_D_ID, OL_O_ID, OL_NUMBER, OL_I_ID, OL_DELIVERY_D, OL_AMOUNT, OL_SUPPLY_W_ID, OL_QUANTITY, OL_DIST_INFO)
FROM '~/cs5424-distributed-database-group-project/cassandra/project-files/data-files/order-line.csv'
WITH DELIMITER=',' AND HEADER=FALSE;

DROP TABLE IF EXISTS stock;
CREATE TABLE stock (
    S_W_ID          int,
    S_I_ID          int,
    S_QUANTITY      int,
    S_YTD           decimal,
    S_ORDER_CNT     int,
    S_REMOTE_CNT    int,
    S_DIST_1        varchar,
    S_DIST_2        varchar,
    S_DIST_3        varchar,
    S_DIST_4        varchar,
    S_DIST_5        varchar,
    S_DIST_6        varchar,
    S_DIST_7        varchar,
    S_DIST_8        varchar,
    S_DIST_9        varchar,
    S_DIST_10       varchar,
    S_DATA          varchar,
    PRIMARY KEY (S_W_ID, S_I_ID)
);
COPY stock (S_W_ID, S_I_ID, S_QUANTITY, S_YTD, S_ORDER_CNT, S_REMOTE_CNT,
    S_DIST_1, S_DIST_2, S_DIST_3, S_DIST_4, S_DIST_5, S_DIST_6, S_DIST_7, S_DIST_8, S_DIST_9, S_DIST_10, S_DATA)
FROM '~/cs5424-distributed-database-group-project/cassandra/project-files/data-files/stock.csv'
WITH DELIMITER=',' AND HEADER=FALSE;

DROP TABLE IF EXISTS stock_counters;
CREATE TABLE stock_counters (
    S_W_ID              int,
    S_I_ID              int,
    S_YTD_CHANGE        counter,
    S_ORDER_CNT_CHANGE  counter,
    S_REMOTE_CNT_CHANGE counter,
    PRIMARY KEY (S_W_ID, S_I_ID)
);

DROP TABLE IF EXISTS related_customers;
CREATE TABLE related_customers (
    C_ID              int,
    C_W_ID            int,
    C_D_ID            int,
    R_ID              int,
    R_W_ID            int,
    R_D_ID            int,
    PRIMARY KEY ((C_W_ID, C_D_ID, C_ID), R_W_ID, R_D_ID, R_ID)
);

DROP TABLE IF EXISTS item_orders;
CREATE TABLE item_orders (
    W_ID              int,
    I_ID              int,
    O_ID              int,
    D_ID              int,
    C_ID              int,
    PRIMARY KEY (W_ID, I_ID, O_ID, D_ID)
);
