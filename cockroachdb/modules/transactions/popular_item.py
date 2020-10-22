from datetime import datetime
from decimal import Decimal
from typing import TypedDict, List, Tuple, Dict

from peewee import fn, Case
from rich.table import Table

from cockroachdb.modules.models import Customer, Item, Order, OrderLine
from cockroachdb.modules.transactions.base import BaseTransaction
from common.logging import console


class PopularItemsOutput(TypedDict):
    """
    Popular items output dict representation
    """

    order_id: int
    entry_date: datetime
    first_name: str
    middle_name: str
    last_name: str
    quantity: Decimal
    item_id: int
    item_name: str


class OrderOutput(TypedDict):
    """
    Order output dict representation
    """

    order_id: int
    entry_date: datetime
    customer_name: str
    popular_items: List[str]


class ItemOutput(TypedDict):
    """
    Item output dict representation
    """

    name: str
    orders: set


class PopularItemsTransaction(BaseTransaction):
    """
    Transaction for querying popular items

    Example:
        popular_items = PopularItemsTransaction(1, 1, 10)
        popular_items.run()
    """

    def __init__(
        self, warehouse_id: int, district_id: int, orders_to_examine: int
    ):
        """
        Initiate a transaction for retrieving popular items
        :param warehouse_id: warehouse identifier
        :param district_id: district identifier
        :param orders_to_examine: number of items to examine
        """
        self.warehouse_id = warehouse_id
        self.district_id = district_id
        self.orders_to_examine = orders_to_examine

    def _execute(self) -> Tuple[List[PopularItemsOutput]]:
        """
        Execute new payment transaction
        :return: relevant output information
        """
        # Get order table joined with customer table
        order_customer_query = (
            Order.select(
                Order.id.alias("order_id"),
                Order.district_id.alias("district_id"),
                Order.warehouse_id.alias("warehouse_id"),
                Order.entry_date.alias("entry_date"),
                Customer.middle_name.alias("middle_name"),
                Customer.first_name.alias("first_name"),
                Customer.last_name.alias("last_name"),
            )
            .join(
                Customer,
                on=(
                    (Order.warehouse_id == Customer.warehouse_id)
                    & (Order.district_id == Customer.district_id)
                    & (Order.customer_id == Customer.id)
                ),
            )
            .where(
                (Order.warehouse_id == self.warehouse_id)
                & (Order.district_id == self.district_id)
            )
            .order_by(Order.entry_date.desc())
            .limit(self.orders_to_examine)
        )

        # Get order lines with maximum quantity, joined with item table
        OrderLineSelfJoin: OrderLine = OrderLine.alias()
        order_line_max_qty_query = OrderLineSelfJoin.select(
            fn.MAX(OrderLineSelfJoin.quantity)
        ).where(
            (OrderLineSelfJoin.warehouse_id == OrderLine.warehouse_id)
            & (OrderLineSelfJoin.district_id == OrderLine.district_id)
            & (OrderLineSelfJoin.order_id == OrderLine.order_id)
        )
        popular_items_query = (
            OrderLine.select(
                order_customer_query.c.order_id,
                order_customer_query.c.entry_date,
                Case(
                    None,
                    (
                        (
                            order_customer_query.c.middle_name.is_null(),
                            fn.CONCAT(
                                order_customer_query.c.first_name,
                                " ",
                                order_customer_query.c.last_name,
                            ),
                        ),
                    ),
                    fn.CONCAT(
                        order_customer_query.c.first_name,
                        order_customer_query.c.middle_name,
                        order_customer_query.c.last_name,
                    ),
                ).alias("customer_name"),
                OrderLine.quantity,
                Item.id.alias("item_id"),
                Item.name.alias("item_name"),
            )
            .join(Item, on=(OrderLine.item_id == Item.id))
            .join(
                order_customer_query,
                on=(
                    (
                        OrderLine.warehouse_id
                        == order_customer_query.c.warehouse_id
                    )
                    & (
                        OrderLine.district_id
                        == order_customer_query.c.district_id
                    )
                    & (OrderLine.order_id == order_customer_query.c.order_id)
                ),
            )
            .where(
                (OrderLine.warehouse_id == self.warehouse_id)
                & (OrderLine.district_id == self.district_id)
                & (OrderLine.quantity.in_(order_line_max_qty_query))
            )
            .order_by(order_customer_query.c.order_id.desc())
        )

        # Process query output
        return ([result for result in popular_items_query.dicts()],)

    def _output_result(self, popular_items: List[PopularItemsOutput]):
        """
        Output execution result
        :param popular_items: list of popular items in PopularItemsOutput format
        :return: None
        """

        def format_popular_item(name: str, quantity: Decimal):
            """
            Format popular item to be printed in console
            :param name: item name
            :param quantity: item quantity
            :return: formatted popular item string
            """
            return f"{name} (QTY: {quantity})"

        console.print(
            f"Popular Items Summary from {self.orders_to_examine} Orders from Warehouse {self.warehouse_id}, District {self.district_id}:".upper()
        )
        order_table = Table(show_header=True, expand=True)
        order_table.add_column("Order Number")
        order_table.add_column("Order Date")
        order_table.add_column("Customer Name")
        order_table.add_column("Popular Items")

        item_table = Table(show_header=True, expand=True)
        item_table.add_column("Item ID")
        item_table.add_column("Item Name")
        item_table.add_column("Percentage of Orders Containing This Item")

        orders: Dict[int, OrderOutput] = {}
        items: Dict[int, ItemOutput] = {}
        for order_line in popular_items:
            order_id = order_line["order_id"]
            item_id, item_name, item_qty = (
                order_line["item_id"],
                order_line["item_name"],
                order_line["quantity"],
            )
            if item_id not in items.keys():
                items[item_id] = {"orders": set(), "name": item_name}
            if order_id not in orders.keys():
                orders[order_id] = {
                    **order_line,
                    "popular_items": [
                        format_popular_item(item_name, item_qty)
                    ],
                }
            else:
                orders[order_id]["popular_items"].append(
                    format_popular_item(item_name, item_qty)
                )
            items[item_id]["orders"].add(order_id)

        for order in orders.values():
            order = order
            order_table.add_row(
                str(order["order_id"]),
                order["entry_date"].strftime("%b %d, %Y, %X (UTC)"),
                order["customer_name"],
                "\n".join(order["popular_items"]),
            )

        for item_id, item_output in sorted(
            items.items(),
            key=lambda item: len(item[1]["orders"]) * 1.0 / len(orders),
            reverse=True,
        ):
            percentage = len(item_output["orders"]) * 1.0 / len(orders)
            item_table.add_row(
                str(item_id), item_output["name"], "{:2.2%}".format(percentage)
            )

        console.print(order_table)
        console.print(item_table)

    @property
    def transaction_name(self):
        """
        Transaction name
        :return: transaction name
        """
        return "popular_items"
