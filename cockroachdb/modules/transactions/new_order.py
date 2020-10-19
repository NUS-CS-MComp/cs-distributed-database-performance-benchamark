from typing import List, Tuple, TypedDict

from cockroachdb.modules.connection import database
from cockroachdb.modules.models import (
    Customer,
    District,
    Item,
    Order,
    OrderLine,
    Stock,
    Warehouse,
)
from cockroachdb.modules.transactions.base import BaseTransaction
from common.logging import logger


class NewOrderItemInput(TypedDict):
    id: int
    supplier_warehouse_id: int
    quantity: int


class NewOrderItemOutput(NewOrderItemInput):
    name: str
    order_line_amount: float
    stock: int


class NewOrderTransaction(BaseTransaction):
    def __init__(
        self,
        customer_identifier: Tuple[int, int, int],
        num_items: int,
        item_number: List[int],
        supplier_warehouse: List[int],
        quantity: List[int],
    ):
        (
            self.warehouse_id,
            self.district_id,
            self.customer_id,
        ) = customer_identifier
        self.items = self._build_item_list(
            num_items, item_number, supplier_warehouse, quantity
        )

    @database.atomic()
    def execute(self):
        warehouse = Warehouse.get_by_id(Warehouse.id)
        warehouse_district = District.get(
            (District.warehouse_id == self.warehouse_id)
            & (District.id == self.district_id)
        )
        customer = Customer.get_by_id(
            (self.warehouse_id, self.district_id, self.customer_id)
        )

        order: Order = Order.create(
            id=warehouse_district.next_order_id,
            warehouse_id=self.warehouse_id,
            district_id=self.district_id,
            customer_id=self.customer_id,
            carrier_id=None,
            order_line_count=len(self.items),
            all_local=int(
                all(
                    item["supplier_warehouse_id"] == self.warehouse_id
                    for item in self.items
                )
            ),
        )

        District.update(next_order_id=District.next_order_id + 1).where(
            (District.warehouse_id == self.warehouse_id)
            & (District.id == self.district_id)
        ).execute()

        total_amount = 0
        items_updated: List[NewOrderItemOutput] = []
        for index, item in enumerate(self.items):
            item_stock: Stock = Stock.get_by_id(
                (self.warehouse_id, item["id"])
            )
            item_record: Item = Item.get_by_id(item["id"])

            adjusted_qty = item_stock.quantity - item["quantity"]
            if adjusted_qty < 10:
                adjusted_qty += 100
            Stock.update(
                quantity=adjusted_qty,
                ytd=Stock.ytd + item["quantity"],
                order_count=Stock.order_count + 1,
                remote_count=Stock.remote_count
                + (
                    1
                    if item["supplier_warehouse_id"] != self.warehouse_id
                    else 0
                ),
            ).where(
                (Stock.warehouse_id == self.warehouse_id)
                & (Stock.item_id == item["id"])
            ).execute()

            amount = item["quantity"] * item_record.price
            total_amount += amount
            OrderLine.create(
                number=index,
                order_id=order.id,
                warehouse_id=self.warehouse_id,
                district_id=self.district_id,
                item_id=item["id"],
                delivery_date=None,
                amount=amount,
                supplying_warehouse_id=item["supplier_warehouse_id"],
                quantity=item["quantity"],
                dist_info=f"S_DIST_{self.district_id}",
            )

            items_updated.append(
                {
                    **item,
                    "name": item_record.name,
                    "order_line_amount": amount,
                    "stock": adjusted_qty,
                }
            )

        total_amount = (
            total_amount
            * (1 + warehouse_district.tax + warehouse.tax)
            * (1 - customer.discount)
        )

        identifier = (
            f"({self.warehouse_id}, {self.district_id}, {self.customer_id})"
        )
        logger.info(
            f"""
            Customer: ({identifier}) {customer.last_name} {customer.credit} {customer.discount}
            Warehouse/District Tax Rate: {warehouse.tax}/{warehouse_district.tax}
            Order: {order.id}, created at {order.entry_date}
            Number of Items/Total Amount: {len(self.items)}/{total_amount}
            ============================
            """
        )
        for index, item in enumerate(items_updated):
            logger.info(
                f"{index}. Item {item['id']} {item['name']} {item['quantity']} {item['order_line_amount']} {item['stock']}"
            )

    @staticmethod
    def _build_item_list(
        num_items: int,
        item_number: List[int],
        supplier_warehouse: List[int],
        quantity: List[int],
    ) -> List[NewOrderItemInput]:
        try:
            assert (
                num_items
                == len(item_number)
                == len(supplier_warehouse)
                == len(quantity)
            )
            return [
                {
                    "id": item_id,
                    "supplier_warehouse_id": warehouse_id,
                    "quantity": qty,
                }
                for item_id, warehouse_id, qty in zip(
                    item_number, supplier_warehouse, quantity
                )
            ]
        except AssertionError:
            logger.exception("New Order inputs are not in correct format")
