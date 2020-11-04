from transactions.utils import do_query

def related_customer(session, w, d, c):
    cql_get_customers = 'SELECT C_W_ID, C_D_ID, C_ID, R_W_ID, R_D_ID, R_ID FROM related_customers ' \
                        'WHERE C_W_ID = {w} AND C_D_ID = {d} AND C_ID = {c}'
    customers = do_query(session, cql_get_customers.format(w=w, d=d, c=c))
    return (w, d, c), [(c.r_w_id, c.r_d_id, c.r_id) for c in customers]
