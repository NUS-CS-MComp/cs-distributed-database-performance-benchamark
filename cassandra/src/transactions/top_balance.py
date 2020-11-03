from transactions.utils import *


def top_balance(session, limit=10):
    cql_get_customers = 'SELECT C_FIRST, C_MIDDLE, C_LAST, C_BALANCE, C_W_ID, C_D_ID, C_ID FROM customer_balances ' \
                        'LIMIT {l}'
    cql_get_warehouse = 'SELECT W_ID, W_NAME FROM warehouse ' \
                        'WHERE W_ID IN {w}'
    cql_get_district = 'SELECT D_ID, D_NAME FROM district ' \
                       'WHERE D_ID IN {d}'
    customers = session.execute(cql_get_customers.format(l=limit))
    w_ids = set([customer.c_w_id for customer in customers])
    d_ids = set([customer.c_d_id for customer in customers])
    warehouses = session.execute(cql_get_warehouse.format(w=get_tuple(tuple(w_ids))))
    districts = session.execute(cql_get_district.format(w=get_tuple(tuple(d_ids))))
    warehouse_names = {}
    district_names = {}
    for w in warehouses:
        warehouse_names[w.w_id] = w.w_name
    for d in districts:
        district_names[d.d_id] = d.d_name
    results = []
    for c in customers:
        entry = {'C_FIRST': c.c_first,
                 'C_MIDDLE': c.c_middle,
                 'C_LAST': c.c_last,
                 'C_BALANCE': c.c_balance,
                 'W_NAME': warehouse_names[c.c_w_id],
                 'D_NAME': district_names[c.c_d_id]}
        results.append(entry)
    return results
