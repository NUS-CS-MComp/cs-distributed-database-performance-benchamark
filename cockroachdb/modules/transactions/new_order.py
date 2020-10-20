from typing import List, Tuple, TypedDict

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
from common.logging import console, logger


class NewOrderItemInput(TypedDict):
    """
    New order input dict representation
    """

    id: int
    supplier_warehouse_id: int
    quantity: int


class NewOrderItemOutput(NewOrderItemInput):
    """
    New order output dict representation
    """

    name: str
    order_line_amount: float
    stock: int


class NewOrderTransaction(BaseTransaction):
    """
    New order transaction

    Example:
        new_order = NewOrderTransaction((1, 1, 1), 3, [1, 2, 3], [1, 1, 1], [3, 4, 5])
        new_order.run()
    """

    def __init__(
        self,
        customer_identifier: Tuple[int, int, int],
        num_items: int,
        item_number: List[int],
        supplier_warehouse: List[int],
        quantity: List[int],
    ):
        """
        Initiate a transaction to create new order
        :param customer_identifier: customer identifier in the form (warehouse, district, customer)
        :param num_items: total number of items
        :param item_number: list of item IDs whose length equals num_items
        :param supplier_warehouse: list of supplier warehouses whose length equals num_items
        :param quantity: list of quantities whose length equals num_items
        """
        (
            self.warehouse_id,
            self.district_id,
            self.customer_id,
        ) = customer_identifier
        self.items = self._build_item_list(
            num_items, item_number, supplier_warehouse, quantity
        )

    def _execute(self):
        """
        Execute new order transaction
        :return: None
        """
        # Get warehouse, district and customer information
        warehouse = Warehouse.get_by_id(Warehouse.id)
        district = District.get(
            (District.warehouse_id == self.warehouse_id)
            & (District.id == self.district_id)
        )
        customer = Customer.get_by_id(
            (self.warehouse_id, self.district_id, self.customer_id)
        )
        order = self._create_new_order(district)
        logger.info(f"Processing new order for customer {customer}")

        # Calculate amounts and update stock and order line records
        total_amount = 0
        items_updated: List[NewOrderItemOutput] = []
        for index, item in enumerate(self.items):
            item_stock: Stock = Stock.get_by_id(
                (self.warehouse_id, item["id"])
            )
            item_record: Item = Item.get_by_id(item["id"])
            adjusted_qty = self._update_stock(item_stock, item)
            item_amount = self._create_new_order_line(
                order, index, item, item_record
            )
            total_amount += item_amount
            items_updated.append(
                {
                    **item,
                    "name": item_record.name,
                    "order_line_amount": item_amount,
                    "stock": adjusted_qty,
                }
            )

        # Process execution output
        total_amount = (
            total_amount
            * (1 + district.tax + warehouse.tax)
            * (1 - customer.discount)
        )
        self._output_result(
            customer, warehouse, district, order, total_amount, items_updated
        )

    def _create_new_order(self, district: District):
        """
        Private method to create new order and update district next order ID
        :param district: District model instance
        :return: Order model instance
        """
        order: Order = Order.create(
            id=district.next_order_id,
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

        return order

    def _update_stock(self, stock: Stock, item: NewOrderItemInput) -> int:
        """
        Update stock information based on new order input
        :param stock: Stock model instance
        :param item: NewOrderItemInput dict item
        :return: adjusted stock quantity
        """
        adjusted_qty = stock.quantity - item["quantity"]
        if adjusted_qty < 10:
            adjusted_qty += 100
        Stock.update(
            quantity=adjusted_qty,
            ytd=Stock.ytd + item["quantity"],
            order_count=Stock.order_count + 1,
            remote_count=Stock.remote_count
            + (1 if item["supplier_warehouse_id"] != self.warehouse_id else 0),
        ).where(
            (Stock.warehouse_id == self.warehouse_id)
            & (Stock.item_id == item["id"])
        ).execute()
        return adjusted_qty

    def _create_new_order_line(
        self,
        order: Order,
        line_number: int,
        item: NewOrderItemInput,
        item_record: Item,
    ):
        """
        Create new order line records
        :param order: Order model instance
        :param line_number: line number as index
        :param item: NewOrderItemInput dict item
        :param item_record: Item model instance
        :return: calculated amount for specific item
        """
        amount = item["quantity"] * item_record.price
        OrderLine.create(
            number=line_number,
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
        return amount

    def _output_result(
        self,
        customer: Customer,
        warehouse: Warehouse,
        district: District,
        order: Order,
        total_amount: float,
        items: List[NewOrderItemOutput],
    ):
        """
        Output execution result
        :param customer: Customer model instance
        :param warehouse: Warehouse model instance
        :param district: District model instance
        :param order: Order model instance
        :param total_amount: Calculated total amount based on tax and discount rate
        :param items: list of NewOrderItemOutput items
        :return: None
        """
        identifier = (
            f"({self.warehouse_id}, {self.district_id}, {self.customer_id})"
        )
        customer_credit = (
            "{:s}".format(customer.credit)
            if customer.credit is not None
            else "N/A"
        )
        customer_discount = "{:.2%}".format(customer.discount)
        console.print(
            f"New Order #{order.id} (Warehouse {warehouse.id}, District {district.id}) Details:".upper()
        )
        console.print(f"Customer Identifier: {identifier}")
        console.print(
            f"Customer Details: {customer.last_name} (Credit: {customer_credit}, Discount: {customer_discount})"
        )
        console.print(
            f"Warehouse/District Tax Rate: {'{:.2%}'.format(warehouse.tax)}/{'{:.2%}'.format(district.tax)}"
        )
        console.print(
            f"Order Number: {order.id}, Created at {order.entry_date.strftime('%b %d, %Y, %X (UTC)')}"
        )
        console.print(
            f"Number of Items/Total Amount: {len(self.items)}/{'{:.2f}'.format(total_amount)}"
        )
        console.print("====================================================")
        console.print(
            "{:>6s} | {:^10s} | {:^6s} | {:^10s} | {:^6s} |".format(
                "Line #", "Item Name", "Qty", "Amount", "Stock"
            )
        )
        order_line_row = "{index:>6d} | {name:^10s} | {quantity:^6.0f} | {amount:^10.2f} | {stock:^6.0f} |".format
        for index, item in enumerate(items):
            console.print(
                order_line_row(
                    index=index + 1,
                    name=item["name"],
                    quantity=item["quantity"],
                    amount=item["order_line_amount"],
                    stock=item["stock"],
                )
            )

    @property
    def transaction_name(self):
        """
        Transaction name
        :return: transaction name
        """
        return "new_order"

    @staticmethod
    def _build_item_list(
        num_items: int,
        item_number: List[int],
        supplier_warehouse: List[int],
        quantity: List[int],
    ) -> List[NewOrderItemInput]:
        """
        Build a list of items, each with stipulated input data
        :param num_items: total number of items
        :param item_number: list of item IDs whose length equals num_items
        :param supplier_warehouse: list of supplier warehouses whose length equals num_items
        :param quantity: list of quantities whose length equals num_items
        :return: list of items in NewOrderItemInput dict format
        """
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
