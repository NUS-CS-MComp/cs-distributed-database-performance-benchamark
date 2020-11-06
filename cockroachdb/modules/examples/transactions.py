from decimal import Decimal

from cockroachdb.modules.transactions import (
    NewOrderTransaction,
    PaymentTransaction,
    DeliveryTransaction,
    OrderStatusTransaction,
    StockLevelTransaction,
    PopularItemsTransaction,
    TopBalanceTransaction,
    RelatedCustomerTransaction,
)
from cockroachdb.modules.transactions.base import BaseTransaction


def run(transaction: BaseTransaction):
    """
    Thunk to transaction
    :param transaction: transaction object
    :return: None
    """
    from cockroachdb.modules.connection import (
        database,
        initialize_cockroach_database,
    )

    database.initialize(initialize_cockroach_database())
    transaction.run()


if __name__ == "__main__":
    from multiprocessing import Pool

    customer = (1, 1, 1)

    transactions = [
        NewOrderTransaction(customer, 3, [1, 2, 3], [1, 1, 1], [1, 1, 1]),
        PaymentTransaction(customer, Decimal(99.99)),
        DeliveryTransaction(1, 100),
        OrderStatusTransaction(customer),
        StockLevelTransaction(1, 1, 100, 2000),
        PopularItemsTransaction(1, 1, 20),
        TopBalanceTransaction(),
        RelatedCustomerTransaction(customer),
    ]

    with Pool(8) as p:
        p.map(run, transactions)
