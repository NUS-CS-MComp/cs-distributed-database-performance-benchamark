from peewee import (
    IntegerField,
    ForeignKeyField,
    CharField,
    FixedCharField,
    TimestampField,
    DecimalField,
)

from cockroachdb.modules.models.base import BaseModel
from cockroachdb.modules.models.district import District
from cockroachdb.modules.models.warehouse import Warehouse


class Customer(BaseModel):
    id = IntegerField(column_name="c_id", primary_key=True, null=False)
    warehouse_id = ForeignKeyField(
        Warehouse, backref="w_id", column_name="c_w_id", null=False
    )
    district_id = ForeignKeyField(
        District, backref="d_id", column_name="c_d_id", null=False
    )
    first_name = CharField(column_name="c_first", max_length=16, null=False)
    middle_name = FixedCharField(
        column_name="c_middle", max_length=2, null=False
    )
    last_name = CharField(column_name="c_last", max_length=16, null=False)
    street_1 = CharField(column_name="c_street_1", max_length=20, null=False)
    street_2 = CharField(column_name="c_street_2", max_length=20)
    city = CharField(column_name="c_city", max_length=20, null=False)
    state = FixedCharField(column_name="c_state", max_length=2)
    zip = FixedCharField(column_name="c_zip", max_length=9, null=False)
    phone_number = FixedCharField(column_name="c_phone", max_length=16)
    since = TimestampField(column_name="c_since", null=False)
    credit = CharField(column_name="c_credit", max_length=2)
    credit_limit = DecimalField(
        column_name="c_credit_lim", max_digits=12, decimal_places=2
    )
    discount = DecimalField(
        column_name="c_discount", max_digits=4, decimal_places=4
    )
    balance = DecimalField(
        column_name="c_balance",
        max_digits=4,
        decimal_places=4,
        null=False,
        default=0.00,
    )
    ytd_payment = DecimalField(
        column_name="c_ytd_payment", null=False, default=0.00
    )
    payment_count = IntegerField(
        column_name="c_payment_cnt", null=False, default=0
    )
    delivery_count = IntegerField(
        column_name="c_delivery_cnt", null=False, default=0
    )
    data = CharField(column_name="c_data", max_length=500)
