CREATE DATABASE IF NOT EXISTS cs5424;

\c cs5424;

DROP TABLE IF EXISTS stock;
DROP TABLE IF EXISTS order_line;
DROP TABLE IF EXISTS "order";
DROP TABLE IF EXISTS customer;
DROP TABLE IF EXISTS district;
DROP TABLE IF EXISTS warehouse;

CREATE TABLE IF NOT EXISTS warehouse
(
    W_ID       INTEGER               NOT NULL PRIMARY KEY,
    W_NAME     CHARACTER VARYING(10) NOT NULL,
    W_STREET_1 CHARACTER VARYING(20) NOT NULL,
    W_STREET_2 CHARACTER VARYING(20),
    W_CITY     CHARACTER VARYING(20) NOT NULL,
    W_STATE    CHARACTER(2),
    W_ZIP      CHARACTER(9)          NOT NULL,
    W_TAX      NUMERIC(4, 4)         NOT NULL,
    W_YTD      NUMERIC(12, 2)        NOT NULL DEFAULT 0.00
);

CREATE TABLE IF NOT EXISTS district
(
    D_ID        INTEGER               NOT NULL,
    D_W_ID      INTEGER               NOT NULL REFERENCES warehouse (W_ID),
    D_NAME      CHARACTER VARYING(10) NOT NULL,
    D_STREET_1  CHARACTER VARYING(20) NOT NULL,
    D_STREET_2  CHARACTER VARYING(20),
    D_CITY      CHARACTER VARYING(20) NOT NULL,
    D_STATE     CHARACTER(2),
    D_ZIP       CHARACTER(9)          NOT NULL,
    D_TAX       NUMERIC(4, 4)         NOT NULL,
    D_YTD       NUMERIC(12, 2)        NOT NULL DEFAULT 0.00,
    D_NEXT_O_ID INTEGER               NOT NULL DEFAULT 1,
    PRIMARY KEY (D_W_ID, D_ID)
);

CREATE TABLE IF NOT EXISTS customer
(
    C_ID           INTEGER               NOT NULL,
    C_W_ID         INTEGER               NOT NULL,
    C_D_ID         INTEGER               NOT NULL,
    C_FIRST        CHARACTER VARYING(16) NOT NULL,
    C_MIDDLE       CHARACTER(2),
    C_LAST         CHARACTER(16)         NOT NULL,
    C_STREET_1     CHARACTER VARYING(20) NOT NULL,
    C_STREET_2     CHARACTER VARYING(20),
    C_CITY         CHARACTER VARYING(20) NOT NULL,
    C_STATE        CHARACTER(2),
    C_ZIP          CHARACTER(9)          NOT NULL,
    C_PHONE        CHARACTER(16),
    C_SINCE        TIMESTAMP             NOT NULL DEFAULT NOW(),
    C_CREDIT       CHARACTER(2),
    C_CREDIT_LIM   NUMERIC(12, 2),
    C_DISCOUNT     NUMERIC(4, 4)         NOT NULL DEFAULT 0.00,
    C_BALANCE      NUMERIC(4, 4)         NOT NULL DEFAULT 0.00,
    C_YTD_PAYMENT  NUMERIC               NOT NULL DEFAULT 0.00,
    C_PAYMENT_CNT  INTEGER               NOT NULL DEFAULT 0,
    C_DELIVERY_CNT INTEGER               NOT NULL DEFAULT 0,
    C_DATA         CHARACTER VARYING(500),
    PRIMARY KEY (C_W_ID, C_D_ID, C_ID),
    FOREIGN KEY (C_W_ID, C_D_ID) references district (D_W_ID, D_ID)
);

CREATE TABLE IF NOT EXISTS "order"
(
    O_ID         INTEGER       NOT NULL,
    O_W_ID       INTEGER       NOT NULL,
    O_D_ID       INTEGER       NOT NULL,
    O_C_ID       INTEGER       NOT NULL,
    O_CARRIER_ID INTEGER,
    O_OL_CNT     NUMERIC(2, 0) NOT NULL,
    O_ALL_LOCAL  NUMERIC(1, 0) NOT NULL,
    O_ENTRY_D    TIMESTAMP     NOT NULL,
    PRIMARY KEY (O_W_ID, O_D_ID, O_ID),
    FOREIGN KEY (O_W_ID, O_D_ID, O_C_ID) REFERENCES customer (C_W_ID, C_D_ID, C_ID)
);

DROP TABLE IF EXISTS item;
CREATE TABLE IF NOT EXISTS item
(
    I_ID    INTEGER               NOT NULL PRIMARY KEY,
    I_NAME  CHARACTER VARYING(24) NOT NULL,
    I_PRICE NUMERIC(5, 2)         NOT NULL,
    I_IM_ID INTEGER,
    I_DATA  CHARACTER VARYING(50)
);

CREATE TABLE IF NOT EXISTS order_line
(
    OL_NUMBER      INTEGER       NOT NULL,
    OL_O_ID        INTEGER       NOT NULL,
    OL_W_ID        INTEGER       NOT NULL,
    OL_D_ID        INTEGER       NOT NULL,
    OL_I_ID        INTEGER       NOT NULL REFERENCES item (I_ID),
    OL_DELIVERY_D  TIMESTAMP,
    OL_AMOUNT      NUMERIC(6, 2) NOT NULL,
    OL_SUPPLY_W_ID INTEGER       NOT NULL,
    OL_QUANTITY    NUMERIC(2, 0) NOT NULL,
    OL_DIST_INFO   CHARACTER VARYING(24),
    PRIMARY KEY (OL_NUMBER, OL_O_ID, OL_W_ID, OL_D_ID),
    FOREIGN KEY (OL_W_ID, OL_D_ID, OL_O_ID) REFERENCES "order" (O_W_ID, O_D_ID, O_ID)
);

CREATE TABLE IF NOT EXISTS stock
(
    S_W_ID       INTEGER       NOT NULL REFERENCES warehouse (W_ID),
    S_I_ID       INTEGER       NOT NULL REFERENCES item (I_ID),
    S_QUANTITY   NUMERIC(4, 0) NOT NULL DEFAULT 0,
    S_YTD        NUMERIC(8, 2) NOT NULL DEFAULT 0.00,
    S_ORDER_CNT  INTEGER       NOT NULL DEFAULT 0,
    S_REMOTE_CNT INTEGER       NOT NULL DEFAULT 0,
    S_DIST_01    CHARACTER(24),
    S_DIST_02    CHARACTER(24),
    S_DIST_03    CHARACTER(24),
    S_DIST_04    CHARACTER(24),
    S_DIST_05    CHARACTER(24),
    S_DIST_06    CHARACTER(24),
    S_DIST_07    CHARACTER(24),
    S_DIST_08    CHARACTER(24),
    S_DIST_09    CHARACTER(24),
    S_DIST_10    CHARACTER(24),
    S_DATA       CHARACTER VARYING(50),
    PRIMARY KEY (S_W_ID, S_I_ID)
);
