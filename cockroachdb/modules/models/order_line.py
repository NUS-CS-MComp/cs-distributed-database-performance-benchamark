from peewee import (
    IntegerField,
    ForeignKeyField,
    TimestampField,
    DecimalField,
    CharField,
    CompositeKey,
)

from cockroachdb.modules.models.base import BaseModel
from cockroachdb.modules.models.item import Item
from cockroachdb.modules.models.order import Order


class OrderLine(BaseModel):
    number = IntegerField(column_name="ol_number", null=False)
    order_id = ForeignKeyField(
        Order, backref="o_id", column_name="ol_o_id", null=False
    )
    warehouse_id = ForeignKeyField(
        Order, backref="o_w_id", column_name="ol_w_id", null=False
    )
    district_id = ForeignKeyField(
        Order, backref="o_d_id", column_name="ol_d_id", null=False
    )
    item_id = ForeignKeyField(
        Item, backref="i_id", column_name="ol_i_id", null=False
    )
    delivery_date = TimestampField(column_name="ol_delivery_d", null=False)
    amount = DecimalField(
        column_name="ol_amount", max_digits=6, decimal_places=2, null=False
    )
    supplying_warehouse_id = IntegerField(
        column_name="ol_supply_w_id", null=False
    )
    quantity = DecimalField(
        column_name="ol_quantity", max_digits=2, decimal_places=0, null=False
    )
    dist_info = CharField(column_name="ol_dist_info", max_length=24)

    class Meta:
        indexes = ((("ol_number", "ol_o_id"), True),)
        primary_key = CompositeKey("ol_number", "ol_o_id")
        table_name = "order_line"
