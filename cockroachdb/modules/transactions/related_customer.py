from typing import Tuple, TypedDict, List

from peewee import Tuple as DBTuple

from cockroachdb.modules.models import Order, OrderLine
from cockroachdb.modules.transactions.base import BaseTransaction


class RelatedCustomerOutput(TypedDict):
    """
    Related customer output dict representation
    """

    warehouse_id: int
    district_id: int
    customer_id: int


class RelatedCustomerTransaction(BaseTransaction):
    """
    Related customer transaction

    Example:
        related_customer = RelatedCustomerTransaction((1, 1, 1))
        related_customer.run()
    """

    def __init__(self, customer_identifier: Tuple[int, int, int]):
        """
        Initiate a transaction to get related customers given customer identifier
        :param customer_identifier: customer identifier in the form (warehouse, district, customer)
        """
        super().__init__()
        (
            self.warehouse_id,
            self.district_id,
            self.customer_id,
        ) = customer_identifier

    def _execute(self) -> List[RelatedCustomerOutput]:
        """
        Execute new order transaction
        :return: relevant output information
        """
        # Get distinct order lines from customer
        customer_orders = Order.select(
            Order.warehouse_id.alias("warehouse_id"),
            Order.district_id.alias("district_id"),
            Order.id.alias("id"),
        ).where(
            (Order.warehouse_id == self.warehouse_id)
            & (Order.district_id == self.district_id)
            & (Order.customer_id == self.customer_id)
        )
        customer_order_lines = (
            OrderLine.select(
                OrderLine.item_id.alias("item_id"),
                OrderLine.warehouse_id.alias("warehouse_id"),
                OrderLine.district_id.alias("district_id"),
                OrderLine.order_id.alias("order_id"),
            )
            .distinct()
            .join(
                customer_orders,
                on=(
                    (customer_orders.c.warehouse_id == OrderLine.warehouse_id)
                    & (customer_orders.c.district_id == OrderLine.district_id)
                    & (customer_orders.c.id == OrderLine.order_id)
                ),
            )
        ).cte("customer_order_lines")

        # Sort out order line pairs from current customer
        customer_order_line_self_join = customer_order_lines.alias(
            "customer_order_lines_self_join"
        )
        customer_order_line_item_pairs = (
            customer_order_lines.select_from(
                customer_order_lines.c.item_id.alias("col_i_id_1"),
                customer_order_line_self_join.c.item_id.alias("col_i_id_2"),
            )
            .join(
                customer_order_line_self_join,
                on=(
                    (
                        customer_order_lines.c.warehouse_id
                        == customer_order_line_self_join.c.warehouse_id
                    )
                    & (
                        customer_order_lines.c.district_id
                        == customer_order_line_self_join.c.district_id
                    )
                    & (
                        customer_order_lines.c.order_id
                        == customer_order_line_self_join.c.order_id
                    )
                ),
            )
            .where(
                customer_order_lines.c.item_id
                < customer_order_line_self_join.c.item_id
            )
            .cte("customer_order_line_item_pairs")
        )

        # Get order lines from other customers containing same items
        other_order_line_with_same_item = (
            OrderLine.select(
                OrderLine.item_id.alias("item_id"),
                OrderLine.warehouse_id.alias("warehouse_id"),
                OrderLine.district_id.alias("district_id"),
                OrderLine.order_id.alias("order_id"),
            )
            .distinct()
            .where(
                (OrderLine.warehouse_id != self.warehouse_id)
                & (
                    OrderLine.item_id.in_(
                        customer_order_lines.select(
                            customer_order_lines.c.item_id
                        ).distinct()
                    )
                )
            )
            .cte("other_order_line_with_same_item")
        )
        other_order_line_with_same_item_self_join = (
            other_order_line_with_same_item.alias("ool2")
        )

        # Find common pairs
        related_customers = (
            other_order_line_with_same_item.select_from(
                other_order_line_with_same_item.c.warehouse_id.alias(
                    "warehouse_id"
                ),
                other_order_line_with_same_item.c.district_id.alias(
                    "district_id"
                ),
                Order.customer_id.alias("customer_id"),
            )
            .distinct()
            .join(
                other_order_line_with_same_item_self_join,
                on=(
                    (
                        other_order_line_with_same_item.c.warehouse_id
                        == other_order_line_with_same_item_self_join.c.warehouse_id
                    )
                    & (
                        other_order_line_with_same_item.c.district_id
                        == other_order_line_with_same_item_self_join.c.district_id
                    )
                    & (
                        other_order_line_with_same_item.c.order_id
                        == other_order_line_with_same_item_self_join.c.order_id
                    )
                    & (
                        other_order_line_with_same_item.c.item_id
                        < other_order_line_with_same_item_self_join.c.item_id
                    )
                ),
            )
            .join(
                Order,
                on=(
                    (
                        other_order_line_with_same_item.c.warehouse_id
                        == Order.warehouse_id
                    )
                    & (
                        other_order_line_with_same_item.c.district_id
                        == Order.district_id
                    )
                    & (other_order_line_with_same_item.c.order_id == Order.id)
                ),
            )
            .where(
                DBTuple(
                    other_order_line_with_same_item.c.item_id,
                    other_order_line_with_same_item_self_join.c.item_id,
                ).in_(
                    customer_order_line_item_pairs.select(
                        customer_order_line_item_pairs.c.col_i_id_1,
                        customer_order_line_item_pairs.c.col_i_id_2,
                    )
                )
            )
            .order_by(
                other_order_line_with_same_item.c.warehouse_id,
                other_order_line_with_same_item.c.district_id,
                Order.customer_id,
            )
            .with_cte(
                customer_order_lines,
                customer_order_line_self_join,
                customer_order_line_item_pairs,
                other_order_line_with_same_item,
                other_order_line_with_same_item_self_join,
            )
        )

        return ([query for query in related_customers.dicts()],)

    def _output_result(self, customers: List[RelatedCustomerOutput]):
        """
        Output execution result
        :param customers: related customer in RelatedCustomerOutput form
        :return: None
        """
        self.print(
            f"Related Customer to ({self.warehouse_id}, {self.district_id}, {self.customer_id}):",
            is_heading=True,
        )
        row_data: List[List[str]] = []
        for customer in customers:
            row_data.append(
                [
                    str(customer["warehouse_id"]),
                    str(customer["district_id"]),
                    str(customer["customer_id"]),
                ]
            )
        self.print_table(
            columns=[
                {"header": "Warehouse ID"},
                {"header": "District ID"},
                {"header": "Customer ID"},
            ],
            rows=row_data,
        )

    @property
    def transaction_name(self):
        """
        Transaction name
        :return: transaction name
        """
        return "related_customer"
