from peewee import IntegerField, CharField, DecimalField

from cockroachdb.modules.models.base import BaseModel


class Item(BaseModel):
    id = IntegerField(column_name="i_id", primary_key=True, null=False)
    name = CharField(column_name="i_name", max_length=24, null=False)
    price = DecimalField(
        column_name="i_price", max_digits=5, decimal_places=2, null=False
    )
    image_id = IntegerField(column_name="i_im_id")
    data = CharField(column_name="i_data", max_length=50)
