from typing import Iterable, List, Tuple

from cockroachdb.modules.models import District, OrderLine, Stock
from cockroachdb.modules.transactions.base import BaseTransaction
from common.logging import console


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
        stock_threshold: int,
        num_of_orders: int
    ):
        """
        Initiate a transaction to query stock level information
        :param warehouse_id: warehouse id
        :param district_id: district id
        :param stock_threshold: threshold for the stock level
        :param num_of_orders: number of last orders to be examined
        """
        self.warehouse_id = warehouse_id
        self.district_id = district_id
        self.stock_threshold = stock_threshold
        self.num_of_orders = num_of_orders

    def _execute(self) -> Tuple[int]:
        """
        Execute stock level transaction
        :return: number of items with lower stock quantity than threshold
        """
        # Retrieve district
        district: District = District.get(
            (District.warehouse_id == self.warehouse_id)
            & (District.id == self.district_id)
        )

        # get all stocks fulfing requrements        
        stock_query: Iterable[Stock] = (Stock
                                        .select(Stock.item_id)
                                        .join(OrderLine, on = ((Stock.warehouse_id == OrderLine.warehouse_id)
                                                               & (Stock.item_id == OrderLine.item_id)))
                                        .where(
                                            (OrderLine.warehouse_id == self.warehouse_id)
                                            & (OrderLine.district_id == self.district_id)
                                            & (OrderLine.order_id >= (district.next_order_id - self.num_of_orders ))
                                            & (Stock.quantity < self.stock_threshold )
                                            ))
        
        stocks: List[Stock] = [
            stock for stock in stock_query
        ]
        
        items = []
        for stock in stocks:
            items.append(str(stock.item_id))

        # return amount of unique ites
        return (len(set(items)),)



    def _output_result(
        self, num_of_items: int,
    ):
        """
        Output execution result 
        :param num_of_items
        :return: None
        """
        console.print(
            "Number of items in stock where its stock quantity at the warehouse is smaller than threshold: " + str(num_of_items)
        )


    @property
    def transaction_name(self):
        """
        Transaction name
        :return: transaction name
        """
        return "stock level"
