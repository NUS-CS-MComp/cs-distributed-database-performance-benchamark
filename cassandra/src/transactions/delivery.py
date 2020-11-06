#!/usr/bin/env python3
from multiprocessing.pool import ThreadPool
from multiprocessing import Process
import threading
from datetime import datetime
from decimal import Decimal
from transactions import utils


def delivery(session, w_id, carrier_id):
    def handle_district(district_no):
        rows = utils.do_query(session, 
            '''
            SELECT MIN(O_ID), O_C_ID FROM orders WHERE O_W_ID = %s AND O_D_ID = %s AND O_CARRIER_ID = 'null' ALLOW FILTERING
            ''',
            (w_id, district_no)
        )
        n = None; c = None
        for row in rows:
            n = row[0]; c = row[1]
            break
        if n == None:   # no undelivered orders in this district
            return
        utils.do_query(session, 
            '''
            UPDATE orders SET O_CARRIER_ID = '%s'
            WHERE O_W_ID = %s AND O_D_ID = %s AND O_ID = %s
            ''',
            (carrier_id, w_id, district_no, n)
        )
        current_datetime = datetime.now()
        current_datetime_str = current_datetime.strftime('%Y-%m-%d %H:%M:%S.%f')
        ol_cnt = utils.single_select(session, 'SELECT O_OL_CNT FROM orders WHERE O_W_ID = %s AND O_D_ID = %s AND O_ID = %s', (w_id, district_no, n))
        for i in range(1, ol_cnt+1):
            utils.do_query(session, 
                '''
                UPDATE order_line
                SET OL_DELIVERY_D = %s
                WHERE OL_W_ID = %s AND OL_D_ID = %s AND OL_O_ID = %s AND OL_NUMBER = %s
                ''',
                (current_datetime_str, w_id, district_no, n, i)
            )
        sum_ol_amount = utils.single_select(session,
            '''
            SELECT SUM(OL_AMOUNT) FROM order_line
            WHERE OL_W_ID = %s AND OL_D_ID = %s AND OL_O_ID = %s
            ''',
            (w_id, district_no, n)
        )
        utils.do_query(session, 
            '''
            UPDATE customer_counters
            SET C_BALANCE_CHANGE = C_BALANCE_CHANGE + %s,
                C_DELIVERY_CNT_CHANGE = C_DELIVERY_CNT_CHANGE + 1
            WHERE C_W_ID = %s AND C_D_ID = %s AND C_ID = %s
            ''',
            (int(sum_ol_amount * 100), w_id, district_no, c)
        )
        balance = utils.single_select(session, 'SELECT C_BALANCE FROM customer_initial WHERE C_W_ID = %s AND C_D_ID = %s AND C_ID = %s', (w_id, district_no, c))
        balance += Decimal(utils.single_select(session, 'SELECT C_BALANCE_CHANGE FROM customer_counters WHERE C_W_ID = %s AND C_D_ID = %s AND C_ID = %s',
            (w_id, district_no, c))) / Decimal(100)
        utils.do_query(session, 'UPDATE customer SET C_BALANCE = %s WHERE C_W_ID = %s AND C_D_ID = %s AND C_ID = %s', (balance, w_id, district_no, c))

    with ThreadPool(10) as pool:
        pool.map(handle_district, range(1, 11))
    
    return None
