from peewee import IntegerField, ForeignKeyField, DecimalField, TimestampField

from cockroachdb.modules.models.base import BaseModel
from cockroachdb.modules.models.customer import Customer
from cockroachdb.modules.models.district import District
from cockroachdb.modules.models.warehouse import Warehouse


class Order(BaseModel):
    id = IntegerField(column_name="o_id", primary_key=True, null=False)
    warehouse_id = ForeignKeyField(
        Warehouse,
        backref="w_id",
        column_name="o_w_id",
        unique=True,
        null=False,
    )
    district_id = ForeignKeyField(
        District, backref="d_id", column_name="o_d_id", unique=True, null=False
    )
    customer_id = ForeignKeyField(
        Customer, backref="c_id", column_name="o_c_id", unique=True, null=False
    )
    carrier_id = IntegerField(column_name="o_carrier_id", null=False)
    order_line_count = DecimalField(
        column_name="o_ol_cnt", max_digits=2, decimal_places=0, null=False
    )
    all_local = DecimalField(
        column_name="o_all_local", max_digits=1, decimal_places=0
    )
    entry_date = TimestampField(column_name="o_entry_d")
