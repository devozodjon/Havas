from django.db.models.signals import pre_save
from django.dispatch import receiver

from apps.products.models import ProductsModel


@receiver(pre_save,sender=ProductsModel)
def update_price(sender,instance,**kwargs):
    instance.real_price = 100