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

    output = {}
    output['EXP_NO'] = int(sys.argv[1])
    output['W_YTD'] = single_select(session, 'SELECT SUM(W_YTD) FROM warehouse')
    output['W_YTD'] += single_select(session, 'SELECT SUM(W_YTD_CHANGE) FROM warehouse_counters') / Decimal(100)
    output['D_YTD'] = single_select(session, 'SELECT SUM(D_YTD) FROM district')
    output['D_YTD'] += single_select(session, 'SELECT SUM(D_YTD_CHANGE) FROM district_counters') / Decimal(100)
    output['D_NEXT_O_ID'] = single_select(session, 'SELECT SUM(D_O_ID_OFST) FROM district')
    output['D_NEXT_O_ID'] += single_select(session, 'SELECT SUM(D_O_COUNTER) FROM district_counters')
    output['C_BALANCE'] = single_select(session, 'SELECT SUM(C_BALANCE) FROM customer')
    output['C_YTD_PAYMENT'] = single_select(session, 'SELECT SUM(C_YTD_PAYMENT) FROM customer')
    output['C_YTD_PAYMENT'] += single_select(session, 'SELECT SUM(C_YTD_PAYMENT_CHANGE) FROM customer_counters') / 100
    output['C_PAYMENT_CNT'] = single_select(session, 'SELECT SUM(C_PAYMENT_CNT) FROM customer')
    output['C_PAYMENT_CNT'] += single_select(session, 'SELECT SUM(C_PAYMENT_CNT_CHANGE) FROM customer_counters')
    output['C_DELIVERY_CNT'] = single_select(session, 'SELECT SUM(C_DELIVERY_CNT) FROM customer')
    output['C_DELIVERY_CNT'] += single_select(session, 'SELECT SUM(C_DELIVERY_CNT_CHANGE) FROM customer_counters')
    output['O_ID'] = single_select(session, 'SELECT MAX(O_ID) FROM orders')
    output['O_OL_CNT'] = single_select(session, 'SELECT SUM(O_OL_CNT) FROM orders')
    output['OL_AMOUNT'] = single_select(session, 'SELECT SUM(OL_AMOUNT) FROM order_line')
    output['OL_QUANTITY'] = single_select(session, 'SELECT SUM(OL_QUANTITY) FROM order_line')
    output['S_QUANTITY'] = single_select(session, 'SELECT SUM(S_QUANTITY) FROM stock')
    output['S_YTD'] = single_select(session, 'SELECT SUM(S_YTD) FROM warehouse')
    output['S_YTD'] += single_select(session, 'SELECT SUM(S_YTD_CHANGE) FROM warehouse_counters') / Decimal(100)
    output['S_ORDER_CNT'] = single_select(session, 'SELECT SUM(S_ORDER_CNT) FROM warehouse')
    output['S_ORDER_CNT'] += single_select(session, 'SELECT SUM(S_ORDER_CNT_CHANGE) FROM warehouse_counters')
    output['S_REMOTE_CNT'] = single_select(session, 'SELECT SUM(S_REMOTE_CNT) FROM warehouse')
    output['S_REMOTE_CNT'] += single_select(session, 'SELECT SUM(S_REMOTE_CNT_CHANGE) FROM warehouse_counters')

    result = pd.DataFrame(output)
    result.to_csv('db-state.csv', index=False, header=False)
