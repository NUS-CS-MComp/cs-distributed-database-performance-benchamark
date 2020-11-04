from multiprocessing.pool import ThreadPool
from functools import partial
from collections import defaultdict
import time

from transactions.new_order import populate_related_customers
from transactions.utils import *

counter = 0
start_time = 0

def work(session, cql, bucket, order):
    global counter
    global start_time
    for i in bucket[(order.o_w_id, order.o_d_id, order.o_id)]:
        do_query(session, cql, (order.o_w_id, i, order.o_id, order.o_d_id, order.o_c_id), 'write')
    populate_related_customers(session, order.o_w_id, order.o_d_id, order.o_c_id, bucket[order.o_id])
    counter += 1
    if counter % 1000 == 0:
        batch_time = time.time()
        elapsed = batch_time - start_time
        throughput = counter * 1.0 / elapsed
        print("number of preprocessed orders: ", counter)
        print("throughput: %s orders per second" % ("{:.2f}".format(throughput)))


def preprocess_related_customer(session):
    global start_time
    bucket = defaultdict(list)
    orders = session.execute('SELECT O_W_ID, O_D_ID, O_ID, O_C_ID FROM orders')
    order_lines = session.execute('SELECT OL_W_ID, OL_D_ID, OL_O_ID, OL_I_ID FROM order_line')
    for ol in order_lines:
        bucket[(ol.ol_w_id, ol.ol_d_id, ol.ol_o_id)].append(ol.ol_i_id)
    print("order lines grouped")
    pool = ThreadPool(16)
    start_time = time.time()
    cql = session.prepare("INSERT INTO item_orders (W_ID, I_ID, O_ID, D_ID, C_ID) VALUES (?, ?, ?, ?, ?)")
    pool.map(partial(work, session, cql, bucket), orders)
