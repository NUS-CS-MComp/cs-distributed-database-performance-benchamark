from datetime import datetime

from peewee import IntegerField, DecimalField, DateTimeField, CompositeKey, SQL

from cockroachdb.modules.models.base import BaseModel


class Order(BaseModel):
    id = IntegerField(column_name="o_id", null=False)
    warehouse_id = IntegerField(
        column_name="o_w_id",
        null=False,
    )
    district_id = IntegerField(column_name="o_d_id", null=False)
    customer_id = IntegerField(column_name="o_c_id", null=False)
    carrier_id = IntegerField(column_name="o_carrier_id", null=False)
    order_line_count = DecimalField(
        column_name="o_ol_cnt", max_digits=2, decimal_places=0, null=False
    )
    all_local = DecimalField(
        column_name="o_all_local", max_digits=1, decimal_places=0
    )
    entry_date = DateTimeField(
        column_name="o_entry_d", default=datetime.utcnow()
    )

    @property
    def formatted_entry_date(self):
        """
        Getter for formatted entry date
        :return: formatted entry date
        """
        return self.entry_date.strftime("%b %d, %Y, %X (UTC)")

    class Meta:
        primary_key = CompositeKey("warehouse_id", "district_id", "id")
        constraints = [
            SQL(
                "FOREIGN KEY (o_w_id, o_d_id, o_c_id) "
                "REFERENCES customer (c_w_id, c_d_id, c_id)"
            )
        ]
