#!/usr/bin/env python3
from datetime import datetime
from transactions import utils
from collections import Counter


def new_order(session, w_id, d_id, c_id, num_items, item_number, supplier_warehouse, quantity, run_rc=True):
    # Step 1
    n = 0
    n = utils.single_select(session, 'SELECT D_O_ID_OFST from district WHERE D_W_ID = %s AND D_ID = %s', (w_id, d_id))
    n += utils.single_select(session, 'SELECT D_O_COUNTER from district_counters WHERE D_W_ID = %s AND D_ID = %s', (w_id, d_id))

    # Step 2
    session.execute('UPDATE district_counters SET D_O_COUNTER = D_O_COUNTER + 1 WHERE D_W_ID = %s AND D_ID = %s', (w_id, d_id))

    # Step 3
    all_local = 1
    for i in range(num_items):
        if supplier_warehouse[i] != w_id:
            all_local = 0
            break
    current_datetime = datetime.now()
    session.execute(
        '''
        INSERT INTO orders (O_ID, O_D_ID, O_W_ID, O_C_ID, O_ENTRY_D, O_CARRIER_ID, O_OL_CNT, O_ALL_LOCAL)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ''',
        (n, d_id, w_id, c_id, datetime.now(), None, num_items, all_local)
    )

    # Step 4 & 5
    total_amount = 0
    item_amount = []
    adjusted_qty = []
    for i in range(num_items):
        # Step 5a
        s_quantity = utils.single_select(session, 'SELECT S_QUANTITY FROM stock WHERE S_W_ID = %s AND S_I_ID = %s',
            (supplier_warehouse[i], item_number[i]))
        # Step 5b
        adjusted_qty.append(s_quantity - quantity[i])
        # Step 5c
        if adjusted_qty[i] < 10:
            adjusted_qty[i] += 100
        # Step 5d
        session.execute('UPDATE stock SET S_QUANTITY = %s WHERE S_W_ID = %s AND S_I_ID = %s',
            (adjusted_qty[i], supplier_warehouse[i], item_number[i]))
        session.execute(
            '''
            UPDATE stock_counters
            SET S_YTD_CHANGE = S_YTD_CHANGE + %s,
                S_ORDER_CNT_CHANGE = S_ORDER_CNT_CHANGE + 1
            WHERE S_W_ID = %s AND S_I_ID = %s
            ''',
            (quantity[i], supplier_warehouse[i], item_number[i])
        )
        if supplier_warehouse[i] != w_id:
            session.execute(
                '''
                UPDATE stock_counters SET S_REMOTE_CNT_CHANGE = S_REMOTE_CNT_CHANGE + 1
                WHERE S_W_ID = %s AND S_I_ID = %s
                ''',
                (supplier_warehouse[i], item_number[i])
            )
        # Step 5e
        i_price = utils.single_select(session, 'SELECT I_PRICE FROM item WHERE I_ID = %s', (item_number[i],))
        item_amount.append(quantity[i] * i_price)
        # Step 5f
        total_amount += item_amount[i]
        # Step 5g
        dist_name = 'S_DIST_' + str(d_id)
        dist_info = utils.single_select(session, 'SELECT {} FROM stock WHERE S_W_ID = {} AND S_I_ID = {}'.format(dist_name, supplier_warehouse[i], item_number[i]))
        session.execute(
            '''
            INSERT INTO order_line (OL_O_ID, OL_D_ID, OL_W_ID, OL_NUMBER, OL_I_ID, OL_SUPPLY_W_ID, OL_QUANTITY, OL_AMOUNT, OL_DIST_INFO)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''',
            (n, d_id, w_id, i, item_number[i], supplier_warehouse[i], quantity[i], item_amount[i], dist_info)
        )
    
    # Step 6
    w_tax = utils.single_select(session, 'SELECT W_TAX FROM warehouse WHERE W_ID = %s', (w_id,))
    d_tax = utils.single_select(session, 'SELECT D_TAX FROM district WHERE D_W_ID = %s AND D_ID = %s', (w_id, d_id))
    c_discount = utils.single_select(session, 'SELECT C_DISCOUNT FROM customer WHERE C_W_ID = %s AND C_D_ID = %s AND C_ID = %s', (w_id, d_id, c_id))
    total_amount *= (1 + d_tax + w_tax) * (1 - c_discount)

    if run_rc:
        populate_related_customers(session, w_id, d_id, c_id, item_number)

    # Output
    output = {}
    output['w_id'] = w_id
    output['d_id'] = d_id
    output['c_id'] = c_id
    rows = session.execute('SELECT C_LAST, C_CREDIT, C_DISCOUNT FROM customer WHERE C_W_ID = %s AND C_D_ID = %s AND C_ID = %s', (w_id, d_id, c_id))
    for row in rows:
        output['c_last'] = row.c_last
        output['c_credit'] = row.c_credit
        output['c_discount'] = row.c_discount
        break
    output['w_tax'] = w_tax
    output['d_tax'] = d_tax
    output['o_id'] = n
    output['o_entry_d'] = current_datetime
    output['num_items'] = num_items
    output['total_amount'] = total_amount
    output['item_infos'] = []
    for i in range(num_items):
        i_name = utils.single_select(session, 'SELECT I_NAME FROM item WHERE I_ID = %s', (item_number[i],))
        output['item_infos'].append((item_number[i], i_name, supplier_warehouse[i], quantity[i], item_amount[i], adjusted_qty[i]))
    return output


def populate_related_customers(session, w_id, d_id, c_id, item_number):
    related_orders = session.execute('SELECT OL_W_ID, OL_D_ID, OL_O_ID FROM order_line WHERE OL_W_ID != %s AND OL_I_ID IN %s ALLOW FILTERING',
                                     (w_id, tuple(item_number)))
    counter = Counter([(order.OL_W_ID, order.OL_D_ID, order.OL_O_ID) for order in related_orders])
    related_orders = [order for order in counter if counter[order] > 1]
    related_customers = session.execute('SELECT DISTINCT O_W_ID, O_D_ID, O_C_ID FROM orders WHERE (O_W_ID, O_D_ID, O_ID) IN %s ALLOW FILTERING',
                                        (tuple(related_orders)))

    query = "INSERT INTO related_customers (C_W_ID, C_D_ID, C_ID, R_W_ID, R_D_ID, R_ID) VALUES (?, ?, ?, ?, ?, ?)"
    prepared = session.prepare(query)
    futures = []
    for rc in related_customers:
        futures.append(session.execute_async(prepared, (w_id, d_id, c_id, rc.O_W_ID, rc.O_D_ID, rc.O_C_ID)))
        futures.append(session.execute_async(prepared, (rc.O_W_ID, rc.O_D_ID, rc.O_C_ID, w_id, d_id, c_id)))
    for f in futures:
        f.result()
