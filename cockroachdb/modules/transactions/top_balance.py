from typing import List, Tuple, TypedDict
from decimal import Decimal
from rich.table import Table
from peewee import fn

from cockroachdb.modules.models import Customer, Warehouse, District
from cockroachdb.modules.transactions.base import BaseTransaction
from common.logging import console

class TopBalanceOutput(TypedDict):
    """
    Top Balance output dict representation
    """
    customer_name: str
    customer_balance: Decimal
    warehouse_name: str
    district_name: str

class TopBalanceTransaction(BaseTransaction):
    """
    Top balance transaction

    Example:
        top_balance = TopBalanceTransaction()
        top_balance.run()
    """

    def __init__(
        self,
    ):
        """
        Initiate a transaction to query customers with top balance
        """
    def _execute(self) -> Tuple[List[TopBalanceOutput]]:
        """
        Execute stock level transaction
        :return: number of items with lower stock quantity than threshold
        """

        # get customers with warehouse and district information
        customer_query = (Customer
                          .select(
                              fn.CONCAT(
                                  Customer.first_name,
                                  Customer.middle_name,
                                  Customer.last_name,
                                  ).alias("customer_name"),
                              Customer.balance.alias("customer_balance"),
                              Warehouse.name.alias("warehouse_name"),
                              District.name.alias("district_name"),
                              )
                          .join(Warehouse, on = (Customer.warehouse_id == Warehouse.id))
                          .join(District, on = (Customer.district_id == District.id))
                          .order_by(Customer.balance.desc())
                          .limit(10)
                          )        
        
        return([result for result in customer_query.dicts()],)


    def _output_result(
        self, top_balance_customers: TopBalanceOutput,
    ):
        """
        Output execution result 
        :param TopBalanceOutput
        :return: None
        """
        result_table = Table(show_header=True, expand=True)
        result_table.add_column("Customer Name")
        result_table.add_column("Customer Balance")
        result_table.add_column("Warehouse Name")
        result_table.add_column("District Name")
        
        for item in TopBalanceOutput:
            result_table.add_row(
                item["customer_name"],
                item["customer_balance"],
                item["warehouse_name"],
                item["district_name"],
            )
            
        console.print(result_table)


    @property
    def transaction_name(self):
        """
        Transaction name
        :return: transaction name
        """
        return "top balance"
