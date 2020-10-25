#!/usr/bin/env python3
from datetime import datetime
from transactions import utils


def delivery(session, w_id, carrier_id):
    for district_no in range(1, 11):
        rows = session.execute(
            '''
            SELECT MIN(O_ID), O_C_ID FROM orders WHERE O_W_ID = %s AND O_D_ID = %s AND O_CARRIER_ID = 'null' ALLOW FILTERING
            ''',
            (w_id, district_no)
        )
        n = 0; c = 0
        for row in rows:
            n = row[0]; c = row[1]
        session.execute(
            '''
            UPDATE orders SET O_CARRIER_ID = '%s'
            WHERE O_W_ID = %s AND O_D_ID = %s AND O_ID = %s
            ''',
            (carrier_id, w_id, district_no, n)
        )
        current_datetime = datetime.now()
        ol_cnt = utils.single_select(session, 'SELECT O_OL_CNT FROM orders WHERE O_W_ID = %s AND O_D_ID = %s AND O_ID = %s', (w_id, district_no, n))
        for i in range(1, ol_cnt+1):
            session.execute(
                '''
                UPDATE order_line
                SET OL_DELIVERY_D = %s
                WHERE OL_W_ID = %s AND OL_D_ID = %s AND OL_O_ID = %s AND OL_NUMBER = %s
                ''',
                (current_datetime.strftime('%Y-%m-%d %H:%M:%S.%f'), w_id, district_no, n, i)
            )
        sum_ol_amount = utils.single_select(session,
            '''
            SELECT SUM(OL_AMOUNT) FROM order_line
            WHERE OL_W_ID = %s AND OL_D_ID = %s AND OL_O_ID = %s
            ''',
            (w_id, district_no, n)
        )
        session.execute(
            '''
            UPDATE customer_counters
            SET C_BALANCE_CHANGE = C_BALANCE_CHANGE + %s,
                C_DELIVERY_CNT_CHANGE = C_DELIVERY_CNT_CHANGE + 1
            WHERE C_W_ID = %s AND C_D_ID = %s AND C_ID = %s
            ''',
            (int(sum_ol_amount * 100), w_id, district_no, c)
        )
    return None
