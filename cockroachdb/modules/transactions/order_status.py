from typing import Tuple, Iterable, List

from peewee import fn
from rich.table import Table

from cockroachdb.modules.models import Customer, Order, OrderLine
from cockroachdb.modules.transactions.base import BaseTransaction
from common.logging import console


class OrderStatusTransaction(BaseTransaction):
    """
    Order status transaction

    Example:
        order_status = OrderStatusTransaction((1, 1, 1))
        order_status.run()
    """

    def __init__(self, customer_identifier: Tuple[int, int, int]):
        """
        Initiate a transaction returning current order status for a specific customer
        :param customer_identifier: customer identifier in the form (warehouse, district, customer)
        """
        (
            self.warehouse_id,
            self.district_id,
            self.customer_id,
        ) = customer_identifier

    def _execute(self) -> Tuple[Customer, Order, List[OrderLine]]:
        """
        Execute order status transaction
        :return: relevant model instance information
        """
        # Get customer information
        customer = Customer.get_by_id(
            (self.warehouse_id, self.district_id, self.customer_id)
        )

        # Subquery to search for order with latest timestamp
        LatestOrder = Order.alias()
        latest_order = (
            LatestOrder.select(fn.MAX(LatestOrder.entry_date).alias("date"))
            .join(
                Customer,
                on=(
                    (LatestOrder.warehouse_id == Customer.warehouse_id)
                    & (LatestOrder.district_id == Customer.district_id)
                    & (LatestOrder.customer_id == Customer.id)
                ),
            )
            .where(
                (Customer.id == self.customer_id)
                & (Customer.warehouse_id == self.warehouse_id)
                & (Customer.district_id == self.district_id)
            )
            .cte("latest_order")
        )

        # Retrieve order with specified latest order CTE
        order: Order = (
            Order.select(Order)
            .join(
                Customer,
                on=(
                    (Order.warehouse_id == Customer.warehouse_id)
                    & (Order.district_id == Customer.district_id)
                    & (Order.customer_id == Customer.id)
                ),
            )
            .where(
                (Customer.id == self.customer_id)
                & (Customer.warehouse_id == self.warehouse_id)
                & (Customer.district_id == self.district_id)
                & (
                    Order.entry_date
                    == (latest_order.select(latest_order.c.date))
                )
            )
            .with_cte(latest_order)
            .get()
        )

        # Get all order line items
        order_line_query: Iterable[OrderLine] = OrderLine.select().where(
            (OrderLine.warehouse_id == self.warehouse_id)
            & (OrderLine.district_id == self.district_id)
            & (OrderLine.order_id == order.id)
        )
        order_lines: List[OrderLine] = [
            order_line for order_line in order_line_query
        ]

        return customer, order, order_lines

    def _output_result(
        self, customer: Customer, order: Order, order_lines: List[OrderLine]
    ):
        """
        Output execution output
        :param customer: Customer model instance
        :param order: Order model instance
        :param order_lines: OrderLine model instances
        :return: None
        """
        console.print(
            f"Order Status for Customer {customer.formatted_name} (End Balance: {customer.balance})".upper()
        )

        # Print order table
        order_table = Table(show_header=True, expand=True)
        order_table.add_column("Order Number")
        order_table.add_column("Entry Date")
        order_table.add_column("Carrier ID")
        order_table.add_row(
            str(order.id), order.formatted_entry_date, str(order.carrier_id)
        )

        # Print order line table
        order_line_table = Table(show_header=True, expand=True)
        order_line_table.add_column("Line #")
        order_line_table.add_column("Supplier Warehouse")
        order_line_table.add_column("Quantity")
        order_line_table.add_column("Amount")
        order_line_table.add_column("Delivery Date", no_wrap=True)
        for order_line in order_lines:
            order_line_table.add_row(
                str(order_line.number),
                str(order_line.supplying_warehouse_id),
                str(order_line.quantity),
                str(order_line.amount),
                order_line.formatted_delivery_date,
            )

        console.print(order_table)
        console.print(order_line_table)

    @property
    def transaction_name(self):
        """
        Transaction name
        :return: transaction name
        """
        return "order_status"
