from decimal import Decimal
from typing import Tuple

from cockroachdb.modules.models import Warehouse, District, Customer
from cockroachdb.modules.models.base import BaseModel
from cockroachdb.modules.transactions.base import BaseTransaction


class PaymentTransaction(BaseTransaction):
    """
    Payment transaction

    Example:
        payment = PaymentTransaction((1, 1, 1), Decimal('99.99'))
        payment.run()
    """

    def __init__(
        self,
        customer_identifier: Tuple[int, int, int],
        payment_amount: Decimal,
    ):
        """
        Initiate a transaction for processing customer payment
        :param customer_identifier: customer identifier in the form (warehouse, district, customer)
        :param payment_amount: payment amount in Decimal format
        """
        super().__init__()
        (
            self.warehouse_id,
            self.district_id,
            self.customer_id,
        ) = customer_identifier
        self.payment_amount = payment_amount

    def _execute(self) -> Tuple[Customer, District, Warehouse]:
        """
        Execute new payment transaction
        :return: relevant model instance information
        """
        # Update warehouse, district YTD amount
        Warehouse.update(ytd=Warehouse.ytd + self.payment_amount).where(
            Warehouse.id == self.warehouse_id
        ).execute()
        District.update(ytd=District.ytd + self.payment_amount).where(
            (District.id == self.district_id)
            & (District.warehouse_id == self.warehouse_id)
        ).execute()

        # Update customer balance, YTD payment and payment count
        Customer.update(
            balance=Customer.balance - self.payment_amount,
            ytd_payment=Customer.ytd_payment + self.payment_amount,
            payment_count=Customer.payment_count + 1,
        ).where(
            (Customer.warehouse_id == self.warehouse_id)
            & (Customer.district_id == self.district_id)
            & (Customer.id == self.customer_id)
        ).execute()

        # Consolidate updated results
        customer: Customer = Customer.get_by_id(
            (self.warehouse_id, self.district_id, self.customer_id)
        )
        district: District = District.get_by_id(
            (self.warehouse_id, self.district_id)
        )
        warehouse: Warehouse = Warehouse.get_by_id(self.warehouse_id)

        return customer, district, warehouse

    def _output_result(
        self, customer: Customer, district: District, warehouse: Warehouse
    ):
        """
        Output execution result
        :param customer: Customer model instance
        :param district: District model instance
        :param warehouse: Warehouse model instance
        :return: None
        """

        def format_address(model: BaseModel):
            return ", ".join(
                filter(
                    lambda x: x is not None,
                    [
                        model.street_1,
                        model.street_2,
                        model.city,
                        model.state,
                        model.zip,
                    ],
                )
            )

        identifier = (
            f"({self.warehouse_id}, {self.district_id}, {self.customer_id})"
        )
        self.print(
            f"New Payment Details from Customer {identifier}:", is_heading=True
        )
        self.print_table(
            columns=[
                {"header": "Name"},
                {"header": "Address"},
                {"header": "Phone"},
                {"header": "Since"},
                {"header": "Credit"},
                {"header": "Credit Limit"},
                {"header": "Discount"},
                {"header": "Balance"},
            ],
            rows=[
                [
                    customer.formatted_name,
                    format_address(customer),
                    customer.phone_number,
                    customer.since.strftime("%b %d, %Y"),
                    customer.credit,
                    customer.credit_limit,
                    "{:.2%}".format(customer.discount),
                    "{:.2f}".format(customer.balance),
                ]
            ],
        )
        self.print(f"Warehouse Address: {format_address(warehouse)}")
        self.print(f"District Address: {format_address(district)}")
        self.print(f"Payment Amount: {'{:.2f}'.format(self.payment_amount)}")

    @property
    def transaction_name(self):
        """
        Transaction name
        :return: transaction name
        """
        return "payment"
