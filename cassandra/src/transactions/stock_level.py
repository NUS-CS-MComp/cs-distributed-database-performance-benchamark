def stock_level(session, warehouse, district, threshold, limit):
    cql_get_orders = 'SELECT O_ID FROM orders ' \
                     'WHERE O_W_ID = {w} AND O_D_ID = {d} ' \
                     'LIMIT {l}'
    cql_get_items = 'SELECT DISTINCT OL_I_ID FROM order_line ' \
                    'WHERE OL_W_ID = {w} AND OL_D_ID = {d} AND OL_O_ID IN {o}'
    cql_get_stocks = 'SELECT S_QUANTITY FROM stock ' \
                     'WHERE S_W_ID = {w} AND S_I_ID IN {i}'
    orders = [order[0] for order in session.execute(cql_get_orders.format(w=warehouse, d=district, l=limit))]
    items = [item[0] for item in session.execute(cql_get_items.format(w=warehouse, d=district, o=tuple(orders)))]
    stocks = [1 for stock in session.execute(cql_get_stocks.format(w=warehouse, i=tuple(items))) if stock[0] < threshold]
    return len(stocks)
