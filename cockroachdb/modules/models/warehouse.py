from peewee import IntegerField, CharField, FixedCharField, DecimalField

from cockroachdb.modules.models.base import BaseModel


class Warehouse(BaseModel):
    id = IntegerField(column_name="w_id", primary_key=True, null=False)
    name = CharField(column_name="w_name", max_length=10, null=False)
    street_1 = CharField(column_name="w_street_1", max_length=20, null=False)
    street_2 = CharField(column_name="w_street_2", max_length=20)
    city = CharField(column_name="w_city", max_length=20, null=False)
    state = FixedCharField(column_name="w_state", max_length=9)
    zip = FixedCharField(column_name="w_zip", max_length=9, null=False)
    tax = DecimalField(
        column_name="w_tax", max_digits=4, decimal_places=4, null=False
    )
    ytd = DecimalField(
        column_name="w_ytd",
        max_digits=12,
        decimal_places=2,
        null=False,
        default=0.00,
    )
