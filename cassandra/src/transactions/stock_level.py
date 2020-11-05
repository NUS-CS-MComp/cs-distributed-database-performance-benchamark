from transactions.utils import *


def stock_level(session, warehouse, district, threshold, limit):
    cql_get_orders = 'SELECT O_ID FROM orders ' \
                     'WHERE O_W_ID = {w} AND O_D_ID = {d} ' \
                     'LIMIT {l}'
    cql_get_items = 'SELECT OL_I_ID FROM order_line ' \
                    'WHERE OL_W_ID = {w} AND OL_D_ID = {d} AND OL_O_ID IN {o}'
    cql_get_stocks = 'SELECT COUNT(*) FROM stock ' \
                     'WHERE S_W_ID = {w} AND S_I_ID IN {i} AND S_QUANTITY < {t} ALLOW FILTERING'
    orders = [order[0] for order in do_query(session, cql_get_orders.format(w=warehouse, d=district, l=limit))]
    items = set([item[0] for item in do_query(session, cql_get_items.format(w=warehouse, d=district, o=get_tuple(orders)))])
    row = do_query(session, cql_get_stocks.format(w=warehouse, i=get_tuple(items), t=threshold))
    return row[0].count
