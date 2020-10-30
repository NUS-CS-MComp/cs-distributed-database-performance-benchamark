#!/usr/bin/env python3
from transactions import utils
from decimal import Decimal


def order_status(session, c_w_id, c_d_id, c_id):
    output = {}

    rows = session.execute('SELECT C_FIRST, C_MIDDLE, C_LAST, C_BALANCE FROM customer WHERE C_W_ID = %s AND C_D_ID = %s AND C_ID = %s', (c_w_id, c_d_id, c_id))
    for row in rows:
        output['c_first'] = row.c_first
        output['c_middle'] = row.c_middle
        output['c_last'] = row.c_last
        output['c_balance'] = row.c_balance
        break
    c_balance_change = utils.single_select(session, 'SELECT C_BALANCE_CHANGE FROM customer_counters WHERE C_W_ID = %s AND C_D_ID = %s AND C_ID = %s', (c_w_id, c_d_id, c_id))
    output['c_balance'] += Decimal(c_balance_change) / Decimal(100)

    rows = session.execute('SELECT O_ID, O_ENTRY_D, O_CARRIER_ID FROM orders WHERE O_W_ID = %s AND O_D_ID = %s LIMIT 1', (c_w_id, c_d_id))  # max O_ID
    for row in rows:
        output['o_id'] = row[0]
        output['o_entry_d'] = row.o_entry_d
        output['o_carrier_id'] = row.o_carrier_id
        break

    o_id = output['o_id']
    rows = session.execute(
        '''
        SELECT OL_I_ID, OL_SUPPLY_W_ID, OL_QUANTITY, OL_AMOUNT, OL_DELIVERY_D
        FROM order_line
        WHERE OL_W_ID = %s AND OL_D_ID = %s AND OL_O_ID = %s
        ''',
        (c_w_id, c_d_id, o_id)
    )
    output['order_lines'] = []
    for row in rows:
        d = {'ol_i_id': row[0], 'ol_supply_w_id': row[1], 'ol_quantity': row[2], 'ol_amount': row[3], 'ol_delivery_d': row[4]}
        output['order_lines'].append(d)

    return output
