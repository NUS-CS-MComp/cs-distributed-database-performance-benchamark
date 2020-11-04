from multiprocessing.pool import ThreadPool
from functools import partial
import threading

from transactions.new_order import populate_related_customers
from transactions.utils import *


def work(order, session):
    print("preprocessing order", order.o_id)
    order_lines = session.execute('SELECT OL_I_ID FROM order_line WHERE OL_W_ID = %s AND OL_D_ID = %s AND OL_O_ID = %s',
                            (order.o_w_id, order.o_d_id, order.o_id))
    ol = [o for o in order_lines]
    cql_insert_item_orders = session.prepare("INSERT INTO item_orders (W_ID, I_ID, O_ID, D_ID, C_ID) VALUES (?, ?, ?, ?, ?)")
    threads = []
    for o in ol:
        # Populate the item_orders table for each item-order pair
        t = threading.Thread(target=do_query,
                             args=(session, cql_insert_item_orders, (order.o_w_id, o.ol_i_id, o.o_id, o.o_d_id, o.o_c_id)))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
    populate_related_customers(session, order.o_w_id, order.o_d_id, order.o_c_id, [o.ol_i_id for o in ol])


def preprocess_related_customer(session):
    orders = session.execute('SELECT O_W_ID, O_D_ID, O_ID, O_C_ID FROM orders')
    pool = ThreadPool(256)
    pool.map(partial(work, session=session), orders)
