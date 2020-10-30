from cassandra.cluster import Cluster
from transactions.new_order import *
from transactions.payment import *
from transactions.delivery import *
from transactions.order_status import *


if __name__ == '__main__':
    cluster = Cluster(['127.0.0.1'], port=6042)
    session = cluster.connect('cs5424')

    # item_number = [68195, 26567]
    # supplier_warehouse = [1, 1]
    # quantity = [1, 5]
    # output = new_order(session, 1, 1, 1279, 2, item_number, supplier_warehouse, quantity)
    # print(output)

    output = payment(session, 1, 2, 186, 22378)
    print(output)

    # output = delivery(session, 1, 7)

    # output = order_status(session, 1, 2, 1081)
    # print(output)
