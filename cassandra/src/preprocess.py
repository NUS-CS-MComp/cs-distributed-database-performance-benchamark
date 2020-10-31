from multiprocessing.pool import ThreadPool
from functools import partial
# import site
# import os
#
# here = os.path.abspath(os.path.dirname(__file__))
# site.addsitedir(os.path.dirname(here))

from transactions.new_order import populate_related_customers


def work(order, session):
    items = session.execute('SELECT OL_I_ID FROM order_line WHERE OL_W_ID = %s AND OL_D_ID = %s AND OL_O_ID = %s',
                            (order.O_W_ID, order.O_D_ID, order.O_ID))
    populate_related_customers(session, order.O_W_ID, order.O_D_ID, order.O_C_ID, tuple([item.OL_I_ID for item in items]))


def preprocess_related_customer(session):
    orders = session.execute('SELECT O_W_ID, O_D_ID, O_ID, O_C_ID FROM orders')
    pool = ThreadPool(256)
    pool.map(partial(work, session=session), orders)
