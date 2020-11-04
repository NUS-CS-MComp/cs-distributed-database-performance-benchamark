from datetime import datetime

from peewee import fn, Tuple as DBTuple

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
        # Find next available order ID for delivery
        try:
            next_delivery_order_inner: Order = (
                Order.select(
                    Order.district_id.alias("district_id"),
                    fn.MIN(Order.id).alias("order_id"),
                )
                .where(
                    Order.carrier_id.is_null()
                    & (Order.warehouse_id == self.warehouse_id)
                )
                .group_by(Order.district_id)
            )
            next_delivery_order: Order = (
                Order.select(
                    Order.district_id.alias("district_id"),
                    Order.id.alias("order_id"),
                    Order.customer_id.alias("customer_id"),
                )
                .where(
                    (Order.warehouse_id == self.warehouse_id)
                    & DBTuple(Order.district_id, Order.id).in_(
                        next_delivery_order_inner
                    )
                )
                .cte("next_delivery_order")
            )
        except Order.DoesNotExist:
            return

        # Retrieve order and order line details
        order_line: OrderLine = (
            OrderLine.select(
                fn.SUM(OrderLine.amount).alias("amount"),
                OrderLine.district_id.alias("district_id"),
                OrderLine.order_id.alias("order_id"),
            )
            .where(
                (OrderLine.warehouse_id == self.warehouse_id)
                & (
                    DBTuple(OrderLine.district_id, OrderLine.order_id).in_(
                        next_delivery_order.select_from(
                            next_delivery_order.c.district_id,
                            next_delivery_order.c.order_id,
                        )
                    )
                )
            )
            .group_by(OrderLine.district_id, OrderLine.order_id)
            .cte("order_line")
        )

        # Update associated order line items
        OrderLine.update(delivery_date=datetime.utcnow()).where(
            (OrderLine.warehouse_id == self.warehouse_id)
            & (
                DBTuple(OrderLine.district_id, OrderLine.order_id).in_(
                    next_delivery_order.select_from(
                        next_delivery_order.c.district_id,
                        next_delivery_order.c.order_id,
                    )
                )
            )
        ).with_cte(next_delivery_order).execute()

        # Update customer balance and delivery count
        Customer.update(
            balance=Customer.balance + order_line.c.amount,
            delivery_count=Customer.delivery_count + 1,
        ).where(
            (Customer.warehouse_id == self.warehouse_id)
            & (Customer.district_id == order_line.c.district_id)
            & (
                DBTuple(Customer.district_id, Customer.id).in_(
                    next_delivery_order.select_from(
                        next_delivery_order.c.district_id,
                        next_delivery_order.c.customer_id,
                    )
                )
            )
        ).with_cte(
            order_line
        ).from_(
            order_line
        ).execute()

        # Update order carrier ID
        Order.update(carrier_id=self.carrier_id).where(
            (Order.warehouse_id == self.warehouse_id)
            & (
                DBTuple(Order.district_id, Order.id).in_(
                    next_delivery_order.select_from(
                        next_delivery_order.c.district_id,
                        next_delivery_order.c.order_id,
                    )
                )
            )
        ).with_cte(next_delivery_order).execute()

    @property
    def transaction_name(self):
        """
        Transaction name
        :return: transaction name
        """
        return "delivery"
