from cassandra import ConsistencyLevel
from cassandra.cluster import Cluster, ExecutionProfile, EXEC_PROFILE_DEFAULT
from decimal import Decimal
import pandas as pd
import sys


def single_select(session, query, data=None, default=0):
    rows = session.execute(query, data)
    for row in rows:
        if row[0] != None:
            return row[0]
        else:
            return default
    return default


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit('experiment number not specified')

    cluster = Cluster(
        ['127.0.0.1'], port=6042,
        execution_profiles={EXEC_PROFILE_DEFAULT: ExecutionProfile(consistency_level=ConsistencyLevel.ALL, request_timeout=1000.0)}
    )
    session = cluster.connect('cs5424')

    exp_no = int(sys.argv[1])
    w_ytd = single_select(session, 'SELECT SUM(W_YTD) FROM warehouse')
    w_ytd += single_select(session, 'SELECT SUM(W_YTD_CHANGE) FROM warehouse_counters') / Decimal(100)
    d_ytd = single_select(session, 'SELECT SUM(D_YTD) FROM district')
    d_ytd += single_select(session, 'SELECT SUM(D_YTD_CHANGE) FROM district_counters') / Decimal(100)
    d_next_o_id = single_select(session, 'SELECT SUM(D_O_ID_OFST) FROM district')
    d_next_o_id += single_select(session, 'SELECT SUM(D_O_COUNTER) FROM district_counters')
    c_balance = single_select(session, 'SELECT SUM(C_BALANCE) FROM customer')
    c_ytd_payment = single_select(session, 'SELECT SUM(C_YTD_PAYMENT) FROM customer')
    c_ytd_payment += single_select(session, 'SELECT SUM(C_YTD_PAYMENT_CHANGE) FROM customer_counters') / 100
    c_payment_cnt = single_select(session, 'SELECT SUM(C_PAYMENT_CNT) FROM customer')
    c_payment_cnt += single_select(session, 'SELECT SUM(C_PAYMENT_CNT_CHANGE) FROM customer_counters')
    c_delivery_cnt = single_select(session, 'SELECT SUM(C_DELIVERY_CNT) FROM customer')
    c_delivery_cnt += single_select(session, 'SELECT SUM(C_DELIVERY_CNT_CHANGE) FROM customer_counters')
    o_id = single_select(session, 'SELECT MAX(O_ID) FROM orders')
    o_ol_cnt = single_select(session, 'SELECT SUM(O_OL_CNT) FROM orders')
    ol_amount = single_select(session, 'SELECT SUM(OL_AMOUNT) FROM order_line')
    ol_quantity = single_select(session, 'SELECT SUM(OL_QUANTITY) FROM order_line')
    s_quantity = single_select(session, 'SELECT SUM(S_QUANTITY) FROM stock')
    s_ytd = single_select(session, 'SELECT SUM(S_YTD) FROM stock')
    s_ytd += single_select(session, 'SELECT SUM(S_YTD_CHANGE) FROM stock_counters') / Decimal(100)
    s_order_cnt = single_select(session, 'SELECT SUM(S_ORDER_CNT) FROM stock')
    s_order_cnt += single_select(session, 'SELECT SUM(S_ORDER_CNT_CHANGE) FROM stock_counters')
    s_remote_cnt = single_select(session, 'SELECT SUM(S_REMOTE_CNT) FROM stock')
    s_remote_cnt += single_select(session, 'SELECT SUM(S_REMOTE_CNT_CHANGE) FROM stock_counters')
    output = [exp_no, w_ytd, d_ytd, d_next_o_id, c_balance, c_ytd_payment, c_payment_cnt, c_delivery_cnt, o_id, o_ol_cnt, ol_amount, ol_quantity, s_quantity, s_ytd, s_order_cnt, s_remote_cnt]

    result = pd.DataFrame([output])
    csv_name = 'db-state-exp{}.csv'.format(sys.argv[1])
    result.to_csv(csv_name, index=False, header=False)
