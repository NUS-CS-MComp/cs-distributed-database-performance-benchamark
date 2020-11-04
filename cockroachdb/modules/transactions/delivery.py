from datetime import datetime
from decimal import Decimal

from peewee import fn

from cockroachdb.modules.models import Order, OrderLine, Customer
from cockroachdb.modules.transactions.base import BaseTransaction


class DeliveryTransaction(BaseTransaction):
    """
    Delivery transaction

    Example:
        delivery = DeliveryTransaction(1, 100)
        delivery.run()
    """

    DISTRICT_ITER_RANGE = [index + 1 for index in range(10)]

    def __init__(self, warehouse_id: int, carrier_id: int):
        """
        Initiate a transaction for processing customer payment
        :param warehouse_id: warehouse number
        :param carrier_id: carrier identifier
        """
        super().__init__()
        self.warehouse_id = warehouse_id
        self.carrier_id = carrier_id

    def _execute(self):
        """
        Execute new delivery transaction
        :return: None
        """
        for district_id in DeliveryTransaction.DISTRICT_ITER_RANGE:
            # Find next available order ID for delivery
            try:
                next_delivery_order: Order = (
                    Order.select()
                    .where(
                        Order.carrier_id.is_null()
                        & (Order.warehouse_id == self.warehouse_id)
                        & (Order.district_id == district_id)
                    )
                    .order_by(Order.id)
                    .limit(1)
                    .get()
                )
                order_id = next_delivery_order.id
            except Order.DoesNotExist:
                continue

            if order_id is not None:
                # Retrieve order and order line details
                order_line: OrderLine = (
                    OrderLine.select(fn.SUM(OrderLine.amount).alias("amount"))
                    .where(
                        (OrderLine.warehouse_id == self.warehouse_id)
                        & (OrderLine.district_id == district_id)
                        & (OrderLine.order_id == order_id)
                    )
                    .get()
                )

                # Update order carrier ID
                Order.update(carrier_id=self.carrier_id).where(
                    (Order.warehouse_id == self.warehouse_id)
                    & (Order.district_id == district_id)
                    & (Order.id == order_id)
                ).execute()

                # Update associated order line items
                OrderLine.update(delivery_date=datetime.utcnow()).where(
                    (OrderLine.warehouse_id == self.warehouse_id)
                    & (OrderLine.district_id == district_id)
                    & (OrderLine.order_id == order_id)
                ).execute()

                # Update customer balance and delivery count
                Customer.update(
                    balance=Customer.balance + Decimal(order_line.amount),
                    delivery_count=Customer.delivery_count + 1,
                ).where(
                    (Customer.warehouse_id == self.warehouse_id)
                    & (Customer.district_id == district_id)
                    & (Customer.id == next_delivery_order.customer_id)
                ).execute()

    @property
    def transaction_name(self):
        """
        Transaction name
        :return: transaction name
        """
        return "delivery"
