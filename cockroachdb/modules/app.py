"""
Example usage:

from decimal import Decimal
from cockroachdb.modules.transactions import *

if __name__ == '__main__':
    customer = (1, 1, 1)
    transactions = [
        NewOrderTransaction(customer, 3, [1, 3, 5], [1, 1, 1], [1, 1, 1]),
        PaymentTransaction(customer, Decimal(99.99)),
        DeliveryTransaction(1, 100),
        OrderStatusTransaction(customer),
        StockLevelTransaction(1, 1, 100, 2000),
        PopularItemsTransaction(1, 1, 20),
        TopBalanceTransaction(),
        RelatedCustomerTransaction(customer)
    ]
    for transaction in transactions:
        transaction.run()
"""
