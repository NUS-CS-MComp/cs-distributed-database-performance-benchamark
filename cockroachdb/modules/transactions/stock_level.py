from typing import Tuple

from cockroachdb.modules.models import District, Order, OrderLine, Stock
from cockroachdb.modules.transactions.base import BaseTransaction


class StockLevelTransaction(BaseTransaction):
    """
    Stock level transaction

    Example:
        stock_level = StockLevelTransaction(1, 1, 10, 5)
        stock_level.run()
    """

    def __init__(
        self,
        warehouse_id: int,
        district_id: int,
        threshold: int,
        order_offset: int,
    ):
        """
        Initiate a transaction to query stock level information
        :param warehouse_id: warehouse id
        :param district_id: district id
        :param threshold: threshold for the stock level
        :param order_offset: number of last orders to be examined
        """
        super().__init__()
        self.warehouse_id = warehouse_id
        self.district_id = district_id
        self.threshold = threshold
        self.order_offset = order_offset

    def _execute(self) -> Tuple[int]:
        """
        Execute stock level transaction
        :return: number of items with lower stock quantity than threshold
        """
        # Retrieve distinct items from last L orders
        order_lines_from_district = ( 
            OrderLine.select(
                OrderLine.warehouse_id.alias("warehouse_id"),
                OrderLine.item_id.alias("item_id"),
            )
            .join(
                District,
                on=(
                    (OrderLine.warehouse_id == District.warehouse_id)
                    & (OrderLine.district_id == District.id)
                ),
            )
            .distinct()
            .where(
                (OrderLine.warehouse_id == self.warehouse_id)
                & (OrderLine.district_id == self.district_id)
                & (OrderLine.order_id >= District.next_order_id - self.order_offset)
                )
            )
        
        # Get stocks and determine counts of those below threshold
        below_threshold_count = (
            Stock.select(Stock.warehouse_id, Stock.item_id)
            .join(
                order_lines_from_district,
                on=(
                    (Stock.warehouse_id == order_lines_from_district.c.warehouse_id)
                    & (Stock.item_id == order_lines_from_district.c.item_id)
                ),
            )
            .where(Stock.quantity <= self.threshold)
            .count()
        )

        return (below_threshold_count,)

    def _output_result(
        self,
        num_of_items: int,
    ):
        """
        Output execution result
        :param num_of_items
        :return: None
        """
        self.print(
            "Number of items in stock where its stock quantity at the warehouse is smaller than threshold: "
            + str(num_of_items),
            is_heading=True,
        )

    @property
    def transaction_name(self):
        """
        Transaction name
        :return: transaction name
        """
        return "stock level"
