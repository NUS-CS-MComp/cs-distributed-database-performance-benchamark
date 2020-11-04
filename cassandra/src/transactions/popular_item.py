from collections import defaultdict
from transactions.utils import *


def popular_item(session, warehouse, district, limit):
    cql_get_orders = 'SELECT O_ID, O_ENTRY_D, O_C_ID FROM orders ' \
                     'WHERE O_W_ID = {w} AND O_D_ID = {d} ' \
                     'LIMIT {l}'
    cql_get_ols = 'SELECT OL_O_ID, OL_I_ID, OL_QUANTITY FROM order_line ' \
                  'WHERE OL_W_ID = {w} AND OL_D_ID = {d} AND OL_O_ID IN {o}'
    cql_get_items = 'SELECT I_ID, I_NAME FROM item ' \
                    'WHERE I_ID IN {i}'
    cql_get_customer_names = 'SELECT C_ID, C_FIRST, C_MIDDLE, C_LAST FROM customer ' \
                             'WHERE C_W_ID = {w} AND C_D_ID = {d} AND C_ID IN {c}'
    orders = session.execute(cql_get_orders.format(w=warehouse, d=district, l=limit))
    orders = [o for o in orders]
    order_ids = [order.o_id for order in orders]
    customer_ids = [order.o_c_id for order in orders]
    ols = session.execute(cql_get_ols.format(w=warehouse, d=district, o=get_tuple(order_ids)))
    customers = session.execute(cql_get_customer_names.format(w=warehouse, d=district, c=get_tuple(tuple(customer_ids))))

    all_popular_item_ids = set()
    ols_by_order = defaultdict(list)
    popular_items_by_order = defaultdict(list)
    customers_by_id = {}
    item_occurance = defaultdict(int)
    for ol in ols:
        ols_by_order[ol.ol_o_id].append(ol)
    for customer in customers:
        customers_by_id[customer.c_id] = customer
    for id in order_ids:
        quantities = defaultdict(int)
        for ol in ols_by_order[id]:
            quantities[ol.ol_i_id] += ol.ol_quantity
        max_quantity = max([value for _, value in quantities.items()])
        popular_items_in_order = [ol.ol_i_id for ol in ols_by_order[id] if ol.ol_quantity == max_quantity]
        popular_items_by_order[id] = (popular_items_in_order, max_quantity)
        all_popular_item_ids.update(popular_items_in_order)
        for id in popular_items_in_order:
            item_occurance[id] += 1

    items = [item for item in session.execute(cql_get_items.format(i=get_tuple(all_popular_item_ids)))]
    item_by_id = {}
    for item in items:
        item_by_id[item.i_id] = item

    result = {'identifier': (warehouse, district), 'number': limit, 'orders': [], 'popular_items': []}
    for order in orders:
        customer = customers_by_id[order.o_c_id]
        popular_items, quantity = popular_items_by_order[order.o_id]
        entry = {'O_ID': order.o_id,
                 'O_ENTRY_D': order.o_entry_d,
                 'C_FIRST': customer.c_first,
                 'C_MIDDLE': customer.c_middle,
                 'C_LAST': customer.c_last,
                 'popular_items': [{'name': item_by_id[item_id].i_name, 'quantity': quantity}
                                    for item_id in popular_items]}
        result['orders'].append(entry)
    for id in all_popular_item_ids:
        entry = {'name': item_by_id[id].i_name,
                 'percentage': item_occurance[id] * 1.0 / int(limit)}
        result['popular_items'].append(entry)
    return result
