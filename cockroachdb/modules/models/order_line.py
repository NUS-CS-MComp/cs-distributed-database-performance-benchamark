from peewee import (
    IntegerField,
    ForeignKeyField,
    DateTimeField,
    DecimalField,
    CharField,
    CompositeKey,
    SQL,
)

from cockroachdb.modules.models.base import BaseModel
from cockroachdb.modules.models.item import Item


class OrderLine(BaseModel):
    number = IntegerField(column_name="ol_number", null=False)
    order_id = IntegerField(column_name="ol_o_id", null=False)
    warehouse_id = IntegerField(column_name="ol_w_id", null=False)
    district_id = IntegerField(column_name="ol_d_id", null=False)
    item_id = ForeignKeyField(
        Item, backref="i_id", column_name="ol_i_id", null=False
    )
    delivery_date = DateTimeField(column_name="ol_delivery_d", null=False)
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

    @property
    def formatted_delivery_date(self):
        """
        Getter for formatted delivery date
        :return: formatted delivery date
        """
        return (
            None
            if self.delivery_date is None
            else self.delivery_date.strftime("%b %d, %Y, %X (UTC)")
        )

    class Meta:
        primary_key = CompositeKey(
            "number", "order_id", "warehouse_id", "district_id"
        )
        table_name = "order_line"
        constraints = [
            SQL(
                "FOREIGN KEY (ol_w_id, ol_d_id, ol_o_id) "
                "REFERENCES order (o_w_id, o_d_id, o_id)"
            )
        ]
        indexes = (("warehouse_id", "district_id", "order_id"), False)
