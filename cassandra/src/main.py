import sys
import time
import pandas as pd
from decimal import Decimal
from cassandra import ConsistencyLevel
from cassandra.cluster import Cluster, ExecutionProfile
from transactions.new_order import *
from transactions.payment import *
from transactions.delivery import *
from transactions.order_status import *
from transactions.stock_level import *
from transactions.popular_item import *
from transactions.top_balance import *
from transactions.related_customer import *
from preprocess import *


if __name__ == '__main__':
    exec_profile = {}
    if len(sys.argv) < 2:
        sys.exit('Args required!')
    if sys.argv[1] == 'ROWA':
        read_profile = ExecutionProfile(consistency_level=ConsistencyLevel.ONE)
        write_profile = ExecutionProfile(consistency_level=ConsistencyLevel.ALL)
        exec_profile = {'read': read_profile, 'write': write_profile}
    elif sys.argv[1] == 'QUORUM':
        read_profile = ExecutionProfile(consistency_level=ConsistencyLevel.QUORUM)
        write_profile = ExecutionProfile(consistency_level=ConsistencyLevel.QUORUM)
        exec_profile = {'read': read_profile, 'write': write_profile}
    else:
        sys.exit('Argument not valid! (consistency level required)')

    cluster = Cluster(['127.0.0.1'], port=6042, execution_profiles=exec_profile)
    session = cluster.connect('cs5424')

    if len(sys.argv) == 3 and sys.argv[2] == 'preprocess':
        preprocess_related_customer(session)
        sys.exit(0)

    input_data = sys.stdin.readlines()
    nlines = len(input_data)

    latency = []
    nTX = 0
    l = 0

    epoc = time.time()
    counter = 0

    while (l < nlines):
        req = input_data[l].rstrip()
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
            output = new_order(session, w_id, d_id, c_id, m, item_number, supplier_warehouse, quantity, background_rc=True)
            l += m
        elif args[0] == "P":
            c_w_id = int(args[1])
            c_d_id = int(args[2])
            c_id = int(args[3])
            amount = Decimal(args[4])
            output = payment(session, c_w_id, c_d_id, c_id, amount)
        elif args[0] == "D":
            w_id = int(args[1])
            carrier_id = int(args[2])
            output = delivery(session, w_id, carrier_id)
        elif args[0] == "O":
            c_w_id = int(args[1])
            c_d_id = int(args[2])
            c_id = int(args[3])
            output = order_status(session, c_w_id, c_d_id, c_id)
        elif args[0] == "S":
            output = stock_level(session, *args[1:])
        elif args[0] == "I":
            output = popular_item(session, *args[1:])
        elif args[0] == "T":
            output = top_balance(session)
        elif args[0] == "R":
            output = related_customer(session, *args[1:])
        else:
            raise Exception("Invalid transaction type: %s" % args[0])

        latency.append(time.time() - start_time)
        nTX += 1
        l += 1

        #print(counter, req)
        #print(output)
        #counter += 1
        #if counter % 100 == 0:
        #    elapsed = time.time() - epoc
        #    throughput = counter * 1.0 / elapsed
        #    print("throughput: %s transactions per second" % ("{:.2f}".format(throughput)))
    
    df = pd.Series(latency)
    result = {}
    result['nTXs'] = nTX
    result['total'] = df.sum()
    result['throughput'] = nTX / result['total']
    result['average'] = df.mean() * 1000
    result['median'] = df.median() * 1000
    result['95percentile'] = df.quantile(0.95) * 1000
    result['99percentile'] = df.quantile(0.99) * 1000
    l = [result['nTXs'], result['total'], result['throughput'], result['average'], result['median'], result['95percentile'], result['99percentile']]
    l = [str(e) for e in l]
    print(",".join(l))

