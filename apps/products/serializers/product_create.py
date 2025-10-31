
from rest_framework import serializers
from apps.products.models import ProductsModel, ProductCategory


class ProductCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductsModel
        exclude = ['updated_at','created_at','uuid']
        read_only_fields = ['real_price']