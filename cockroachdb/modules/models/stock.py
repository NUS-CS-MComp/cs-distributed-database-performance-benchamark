from peewee import (
    ForeignKeyField,
    DecimalField,
    IntegerField,
    CharField,
    CompositeKey,
)

from cockroachdb.modules.models.base import BaseModel
from cockroachdb.modules.models.item import Item
from cockroachdb.modules.models.warehouse import Warehouse


class Stock(BaseModel):
    warehouse_id = ForeignKeyField(
        Warehouse, backref="w_id", column_name="s_w_id", null=False
    )
    item_id = ForeignKeyField(
        Item, backref="i_id", column_name="s_i_id", null=False
    )
    quantity = DecimalField(
        column_name="s_quantity",
        max_digits=4,
        decimal_places=0,
        null=False,
        default=0,
    )
    ytd = DecimalField(
        column_name="s_ytd",
        max_digits=8,
        decimal_places=2,
        null=False,
        default=0.00,
    )
    order_count = IntegerField(
        column_name="s_order_cnt", null=False, default=0
    )
    remote_count = IntegerField(
        column_name="s_remote_cnt", null=False, default=0
    )
    dist_info_01 = CharField(column_name="s_dist_01", max_length=24)
    dist_info_02 = CharField(column_name="s_dist_02", max_length=24)
    dist_info_03 = CharField(column_name="s_dist_03", max_length=24)
    dist_info_04 = CharField(column_name="s_dist_04", max_length=24)
    dist_info_05 = CharField(column_name="s_dist_05", max_length=24)
    dist_info_06 = CharField(column_name="s_dist_06", max_length=24)
    dist_info_07 = CharField(column_name="s_dist_07", max_length=24)
    dist_info_08 = CharField(column_name="s_dist_08", max_length=24)
    dist_info_09 = CharField(column_name="s_dist_09", max_length=24)
    dist_info_10 = CharField(column_name="s_dist_10", max_length=24)
    data = CharField(column_name="s_data", max_length=50)

    class Meta:
        primary_key = CompositeKey("warehouse_id", "item_id")
