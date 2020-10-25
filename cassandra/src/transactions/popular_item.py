from collections import defaultdict


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
    order_ids = [order.O_ID for order in orders]
    customer_ids = [order.O_C_ID for order in orders]
    ols = session.execute(cql_get_ols.format(w=warehouse, d=district, o=tuple(order_ids)))
    customers = session.execute(cql_get_customer_names.format(w=warehouse, d=district, c=tuple(customer_ids)))

    all_popular_item_ids = set()
    ols_by_order = defaultdict(list)
    popular_items_by_order = defaultdict(list)
    customers_by_id = defaultdict(list)
    item_occurance = defaultdict(int)
    for ol in ols:
        ols_by_order[ol.OL_O_ID].append(ol)
    for customer in customers:
        customers_by_id[customer.C_ID].append(customer)
    for id in order_ids:
        max_quantity = max([ol.OL_QUANTITY for ol in ols_by_order[id]])
        popular_items_in_order = [ol.OL_I_ID for ol in ols_by_order[id] if ol.OL_QUANTITY == max_quantity]
        popular_items_by_order[id] = (popular_items_in_order, max_quantity)
        all_popular_item_ids.update(popular_items_in_order)
        for id in popular_items_in_order:
            item_occurance[id] += 1

    items = [item for item in session.execute(cql_get_items.format(i=tuple(all_popular_item_ids)))]
    item_by_id = {}
    for item in items:
        item_by_id[item.I_ID] = item

    result = {'identifier': (warehouse, district), 'number': limit, 'orders': []}
    for order in orders:
        customer = customers_by_id[order.O_C_ID]
        entry =  {'O_ID': order.O_ID,
                  'O_ENTRY_D': order.O_ENTRY_D,
                  'C_FIRST': customer.C_FIRST,
                  'C_MIDDLE': customer.C_MIDDLE,
                  'C_LAST': customer.C_LAST,
                  'popular_items': [{'name': item_by_id[item_id].I_NAME, 'quantity': max}
                                    for ids, max in popular_items_by_order[order.O_ID]
                                    for item_id in ids]}
        result['orders'].append(entry)
    for id in all_popular_item_ids:
        entry = {'name': item_by_id[id].I_NAME,
                 'percentage': item_occurance[id] * 1.0 / limit}
        result['popular_items'].append(entry)
    return result
