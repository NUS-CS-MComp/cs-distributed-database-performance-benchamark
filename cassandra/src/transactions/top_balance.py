def top_balance(session, limit=10):
    cql_get_customers = 'SELECT C_FIRST, C_MIDDLE, C_LAST, C_BALANCE, C_W_ID, C_D_ID FROM customer ' \
                        'LIMIT {l}'
    cql_get_warehouse = 'SELECT W_ID, W_NAME FROM warehouse ' \
                        'WHERE W_ID IN {w}'
    cql_get_district = 'SELECT D_ID, D_NAME FROM district ' \
                       'WHERE D_ID {d}'
    customers = session.execute(cql_get_customers.format(l=limit))
    w_ids = set([customer.C_W_ID for customer in customers])
    d_ids = set([customer.C_D_ID for customer in customers])
    warehouses = session.execute(cql_get_warehouse.format(w=tuple(w_ids)))
    districts = session.execute(cql_get_district.format(w=tuple(d_ids)))
    warehouse_names = {}
    district_names = {}
    for w in warehouses:
        warehouse_names[w.W_ID] = w.W_NAME
    for d in districts:
        district_names[d.D_ID] = d.D_NAME
    results = []
    for c in customers:
        entry = {'C_FIRST': c.C_FIRST,
                 'C_MIDDLE': c.C_MIDDLE,
                 'C_LAST': c.C_LAST,
                 'C_BALANCE': c.C_BALANCE,
                 'W_NAME': warehouse_names[c.C_W_ID],
                 'D_NAME': district_names[c.C_D_ID]}
        results.append(entry)
    return results
