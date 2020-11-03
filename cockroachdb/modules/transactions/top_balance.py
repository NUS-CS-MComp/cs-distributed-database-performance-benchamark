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
        top_customer_query = (
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
                Customer.warehouse_id.alias("warehouse_id"),
                Customer.district_id.alias("district_id"),
            )
            .order_by(Customer.balance.desc())
            .limit(TopBalanceTransaction.LIMIT)
            .cte("top_customer_query")
        )
        top_balance_query = (
            top_customer_query.select_from(
                top_customer_query.c.customer_name,
                top_customer_query.c.customer_balance,
                Warehouse.name.alias("warehouse_name"),
                District.name.alias("district_name"),
            )
            .join(
                District,
                on=(
                    (
                        top_customer_query.c.warehouse_id
                        == District.warehouse_id
                    )
                    & (top_customer_query.c.district_id == District.id)
                ),
            )
            .join(
                Warehouse,
                on=(top_customer_query.c.warehouse_id == Warehouse.id),
            )
            .order_by(top_customer_query.c.customer_balance.desc())
            .with_cte(top_customer_query)
        )

        return ([result for result in top_balance_query.dicts()],)

    def _output_result(
        self,
        top_balance_customers: List[TopBalanceOutput],
    ):
        """
        Output execution result
        :param top_balance_customers
        :return: None
        """
        self.print(
            "Customers Ranked by Top Balance:",
            is_heading=True,
        )
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
