
from rest_framework import serializers

from apps.products.models import ProductsModel
from apps.shared.mixins.translation_mixins import (
    TranslatedFieldsWriteMixin,
)


class ProductTranslationMixin:
    """Shared configuration for OnBoarding serializers"""
    translatable_fields = ['title', 'description']
    media_fields = ['image']


class ProductCreateSerializer(TranslatedFieldsWriteMixin, serializers.ModelSerializer):
    real_price = serializers.DecimalField(required=False, max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = ProductsModel
        fields = [
            'price', 'real_price',
            'measurement',
            'is_active', 'category', 'discount',
        ]


class ProductListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductsModel
        exclude = ['title', 'description']

