from typing import Tuple, Iterable, List

from cockroachdb.modules.models import Customer, Order, OrderLine
from cockroachdb.modules.transactions.base import BaseTransaction


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
        super().__init__()
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

        # Retrieve latest order
        order: Order = (
            Order.select(Order)
            .where(
                (Order.customer_id == self.customer_id)
                & (Order.warehouse_id == self.warehouse_id)
                & (Order.district_id == self.district_id)
            )
            .order_by(Order.entry_date.desc())
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
        self.print(
            f"Order Status for Customer {customer.formatted_name} (End Balance: {customer.balance}):",
            is_heading=True,
        )

        # Print order table
        self.print_table(
            columns=[
                {"header": "Order Number"},
                {"header": "Entry Date"},
                {"header": "Carrier ID"},
            ],
            rows=[
                [
                    str(order.id),
                    order.formatted_entry_date,
                    str(order.carrier_id),
                ]
            ],
        )

        # Print order line table
        line_items = []
        for order_line in order_lines:
            line_items.append(
                [
                    str(order_line.number),
                    str(order_line.supplying_warehouse_id),
                    str(order_line.quantity),
                    str(order_line.amount),
                    order_line.formatted_delivery_date,
                ]
            )
        self.print_table(
            columns=[
                {"header": "Line #"},
                {"header": "Supplier Warehouse"},
                {"header": "Quantity"},
                {"header": "Amount"},
                {"header": "Delivery Date", "no_wrap": True},
            ],
            rows=line_items,
        )

    @property
    def transaction_name(self):
        """
        Transaction name
        :return: transaction name
        """
        return "order_status"
