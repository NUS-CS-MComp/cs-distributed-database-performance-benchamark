import sys
import time
import pandas as pd
from decimal import Decimal
from cassandra.cluster import Cluster
from transactions.new_order import *
from transactions.payment import *
from transactions.delivery import *
from transactions.order_status import *


if __name__ == '__main__':
    cluster = Cluster(['127.0.0.1'], port=6042)
    session = cluster.connect('cs5424')

    input_data = sys.stdin.readlines()
    nlines = len(input_data)

    latency = []
    nTX = 0
    l = 0
    # while (l < nlines):
    while (l < 200):
        req = input_data[l]
        args = req.split(",")
        start_time = time.time()
        if args[0] == "N":
            c_id = int(args[1])
            w_id = int(args[2])
            d_id = int(args[3])
            m = int(args[4])
            item_number, supplier_warehouse, quantity = [], [], []
            for i in range(m):
                data = input_data[l+i+1]
                args = data.split(",")
                item_number.append(int(args[0]))
                supplier_warehouse.append(int(args[1]))
                quantity.append(int(args[2]))
            output = new_order(session, w_id, d_id, c_id, m, item_number, supplier_warehouse, quantity)
            print(output)
            l += m
        elif args[0] == "P":
            c_w_id = int(args[1])
            c_d_id = int(args[2])
            c_id = int(args[3])
            amount = Decimal(args[4])
            output = payment(session, c_w_id, c_d_id, c_id, amount)
            print(output)
        elif args[0] == "D":
            w_id = int(args[1])
            carrier_id = int(args[2])
            delivery(session, w_id, carrier_id)
        elif args[0] == "O":
            c_w_id = int(args[1])
            c_d_id = int(args[2])
            c_id = int(args[3])
            output = order_status(session, c_w_id, c_d_id, c_id)
            print(output)
        latency.append(time.time() - start_time)
        nTX += 1
        l += 1
    
    df = pd.Series(latency)
    result = {}
    result['nTXs'] = nTX
    result['total'] = df.sum()
    result['throughput'] = nTX / result['total']
    result['average'] = df.mean()
    result['median'] = df.median()
    result['95percentile'] = df.quantile(0.95)
    result['99percentile'] = df.quantile(0.99)
    print(result)
