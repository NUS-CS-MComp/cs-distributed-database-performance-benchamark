from typing import Tuple, TypedDict, List

from cockroachdb.modules.models import Customer, Order, OrderLine
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
        )

        # Get distinct order lines from other customers
        other_customers = Customer.select(
            Customer.warehouse_id.alias("warehouse_id"),
            Customer.district_id.alias("district_id"),
            Customer.id.alias("id"),
        ).where(Customer.warehouse_id != self.warehouse_id)
        other_orders = Order.select(
            Order.warehouse_id.alias("warehouse_id"),
            Order.district_id.alias("district_id"),
            Order.id.alias("id"),
            other_customers.c.id.alias("customer_id"),
        ).join(
            other_customers,
            on=(
                (other_customers.c.warehouse_id == Order.warehouse_id)
                & (other_customers.c.district_id == Order.district_id)
                & (other_customers.c.id == Order.customer_id)
            ),
        )
        other_order_lines = (
            OrderLine.select(
                OrderLine.item_id.alias("item_id"),
                OrderLine.warehouse_id.alias("warehouse_id"),
                OrderLine.district_id.alias("district_id"),
                OrderLine.order_id.alias("order_id"),
                other_orders.c.customer_id.alias("customer_id"),
            )
            .distinct()
            .join(
                other_orders,
                on=(
                    (other_orders.c.warehouse_id == OrderLine.warehouse_id)
                    & (other_orders.c.district_id == OrderLine.district_id)
                    & (other_orders.c.id == OrderLine.order_id)
                ),
            )
        )

        # Sort out order line pairs from both tables
        customer_ol_cte = customer_order_lines.cte("customer_order_lines")
        customer_ol_cte_self_join = customer_ol_cte.alias(
            "customer_order_lines_self_join"
        )
        other_ol_cte = other_order_lines.cte("other_order_lines")
        other_ol_cte_self_join = other_ol_cte.alias(
            "other_order_lines_self_join"
        )

        customer_ol_pairs = (
            customer_ol_cte.select_from(
                customer_ol_cte.c.item_id.alias("col_i_id_1"),
                customer_ol_cte_self_join.c.item_id.alias("col_i_id_2"),
                customer_ol_cte.c.warehouse_id,
                customer_ol_cte.c.district_id,
                customer_ol_cte.c.order_id,
            )
            .join(
                customer_ol_cte_self_join,
                on=(
                    (
                        customer_ol_cte.c.warehouse_id
                        == customer_ol_cte_self_join.c.warehouse_id
                    )
                    & (
                        customer_ol_cte.c.district_id
                        == customer_ol_cte_self_join.c.district_id
                    )
                    & (
                        customer_ol_cte.c.order_id
                        == customer_ol_cte_self_join.c.order_id
                    )
                ),
            )
            .where(
                customer_ol_cte.c.item_id < customer_ol_cte_self_join.c.item_id
            )
        )

        other_customer_ol_pairs = (
            other_ol_cte.select_from(
                other_ol_cte.c.item_id.alias("ool_i_id_1"),
                other_ol_cte_self_join.c.item_id.alias("ool_i_id_2"),
                other_ol_cte.c.warehouse_id,
                other_ol_cte.c.district_id,
                other_ol_cte.c.order_id,
                other_ol_cte.c.customer_id,
            )
            .join(
                other_ol_cte_self_join,
                on=(
                    (
                        other_ol_cte.c.warehouse_id
                        == other_ol_cte_self_join.c.warehouse_id
                    )
                    & (
                        other_ol_cte.c.district_id
                        == other_ol_cte_self_join.c.district_id
                    )
                    & (
                        other_ol_cte.c.order_id
                        == other_ol_cte_self_join.c.order_id
                    )
                ),
            )
            .where(other_ol_cte.c.item_id < other_ol_cte_self_join.c.item_id)
        )

        # Find common pairs
        related_customers = (
            customer_ol_pairs.select_from(
                other_customer_ol_pairs.c.warehouse_id,
                other_customer_ol_pairs.c.district_id,
                other_customer_ol_pairs.c.customer_id,
            )
            .distinct()
            .join(
                other_customer_ol_pairs,
                on=(
                    (
                        customer_ol_pairs.c.col_i_id_1
                        == other_customer_ol_pairs.c.ool_i_id_1
                    )
                    & (
                        customer_ol_pairs.c.col_i_id_2
                        == other_customer_ol_pairs.c.ool_i_id_2
                    )
                ),
            )
            .with_cte(
                customer_ol_cte,
                customer_ol_cte_self_join,
                other_ol_cte,
                other_ol_cte_self_join,
            )
        )

        return ([query for query in related_customers],)

    def _output_result(self, customers: List[RelatedCustomerOutput]):
        """
        Output execution result
        :param customers: related customer in RelatedCustomerOutput form
        :return: None
        """
        self.print(
            f"Related Customer to ({self.warehouse_id}, {self.district_id}, {self.customer_id}):".upper()
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
