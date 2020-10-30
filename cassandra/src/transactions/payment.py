#!/usr/bin/env python3
from transactions import utils
from transactions.utils import Constants


def payment(session, c_w_id, c_d_id, c_id, amount):
    cents = int(amount * 100)
    session.execute('UPDATE warehouse_counters SET W_YTD_CHANGE = W_YTD_CHANGE + %s WHERE W_CONST = %s AND W_ID = %s',
        (cents, Constants.CONST_PARTITION_KEY_WAREHOUSE, c_w_id))
    session.execute('UPDATE district_counters SET D_YTD_CHANGE = D_YTD_CHANGE + %s WHERE D_CONST = %s AND D_W_ID = %s AND D_ID = %s',
        (cents, Constants.CONST_PARTITION_KEY_DISTRICT, c_w_id, c_d_id))
    session.execute(
        '''
        UPDATE customer_counters
        SET C_BALANCE_CHANGE = C_BALANCE_CHANGE - %s,
            C_YTD_PAYMENT_CHANGE = C_YTD_PAYMENT_CHANGE + %s,
            C_PAYMENT_CNT_CHANGE = C_PAYMENT_CNT_CHANGE + 1
        WHERE C_W_ID = %s AND C_D_ID = %s AND C_ID = %s
        ''',
        (cents, cents, c_w_id, c_d_id, c_id)
    )

    output = {}
    rows = session.execute(
        '''
        SELECT C_W_ID, C_D_ID, C_ID, C_FIRST, C_MIDDLE, C_LAST, C_STREET_1, C_STREET_2,
               C_CITY, C_STATE, C_ZIP, C_PHONE, C_SINCE, C_CREDIT, C_CREDIT_LIM, C_DISCOUNT, C_BALANCE
        FROM customer
        WHERE C_W_ID = %s AND C_D_ID = %s AND C_ID = %s
        ''',
        (c_w_id, c_d_id, c_id)
    )
    for row in rows:
        c = row._asdict()
        c['c_balance'] -= amount
        output['customer_info'] = c
        break
    rows = session.execute('SELECT W_STREET_1, W_STREET_2, W_CITY, W_STATE, W_ZIP FROM warehouse WHERE W_CONST = %s AND W_ID = %s',
        (Constants.CONST_PARTITION_KEY_WAREHOUSE, c_w_id))
    for row in rows:
        output['warehouse_info'] = row._asdict()
        break
    rows = session.execute('SELECT D_STREET_1, D_STREET_2, D_CITY, D_STATE, D_ZIP FROM district WHERE D_CONST = %s AND D_W_ID = %s AND D_ID = %s',
        (Constants.CONST_PARTITION_KEY_DISTRICT, c_w_id, c_d_id))
    for row in rows:
        output['district_info'] = row._asdict()
        break
    return output
