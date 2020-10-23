from decimal import Decimal
from typing import List, Tuple, TypedDict

from peewee import fn, Case

from cockroachdb.modules.models import Customer, Warehouse, District
from cockroachdb.modules.transactions.base import BaseTransaction


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

    LIMIT = 10

    def _execute(self) -> Tuple[List[TopBalanceOutput]]:
        """
        Execute stock level transaction
        :return: number of items with lower stock quantity than threshold
        """

        # Get customers with warehouse and district information
        customer_query = (
            Customer.select(
                Case(
                    None,
                    (
                        (
                            Customer.middle_name.is_null(),
                            fn.CONCAT(
                                Customer.first_name,
                                " ",
                                Customer.last_name,
                            ),
                        ),
                    ),
                    fn.CONCAT(
                        Customer.first_name,
                        Customer.middle_name,
                        Customer.last_name,
                    ),
                ).alias("customer_name"),
                Customer.balance.alias("customer_balance"),
                Warehouse.name.alias("warehouse_name"),
                District.name.alias("district_name"),
            )
            .join(
                District,
                on=(
                    (Customer.warehouse_id == District.warehouse_id)
                    & (Customer.district_id == District.id)
                ),
            )
            .join(Warehouse, on=(District.warehouse_id == Warehouse.id))
            .order_by(Customer.balance.desc())
            .limit(TopBalanceTransaction.LIMIT)
        )

        return ([result for result in customer_query.dicts()],)

    def _output_result(
        self,
        top_balance_customers: List[TopBalanceOutput],
    ):
        """
        Output execution result
        :param top_balance_customers
        :return: None
        """
        customers = []
        for item in top_balance_customers:
            customers.append(
                [
                    item["customer_name"],
                    str(item["customer_balance"]),
                    item["warehouse_name"],
                    item["district_name"],
                ]
            )
        self.print_table(
            columns=[
                {"header": "Customer Name"},
                {"header": "Customer Balance"},
                {"header": "Warehouse Name"},
                {"header": "District Name"},
            ],
            rows=customers,
        )

    @property
    def transaction_name(self):
        """
        Transaction name
        :return: transaction name
        """
        return "top balance"
