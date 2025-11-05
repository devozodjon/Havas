from apps.cart.models import CartList

from rest_framework import serializers
from apps.cart.models import CartItem
from apps.products.models import ProductsModel


class CartItemSerializer(serializers.ModelSerializer):
    product = serializers.IntegerField(required=False, allow_null=True)
    product_title = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = [
            'id',
            'shopping_list',
            'product',
            'product_title',
            'custom_title',
            'quantity',
            'measurement',
            'is_checked'
        ]

    def get_product_title(self, obj):
        if obj.product:
            return obj.product.title
        return None

    def validate(self, data):
        product_id = data.get('product')
        custom_title = data.get('custom_title')

        # Ikkalasi ham yo‘q bo‘lsa — xato
        if not product_id and not custom_title:
            raise serializers.ValidationError({
                "non_field_error": "Mahsulot yoki custom_title bo‘lishi kerak."
            })

        return data

    def create(self, validated_data):
        product_id = validated_data.pop('product', None)
        product_instance = None

        # Agar product_id kiritilgan bo‘lsa, uni bazadan izlaymiz
        if product_id:
            product_instance = ProductsModel.objects.filter(id=product_id).first()

        # Agar bazada mavjud bo‘lmasa → product=None qilib qo‘yamiz
        validated_data['product'] = product_instance

        item = CartItem.objects.create(**validated_data)
        return item

    def to_representation(self, instance):
        rep = super().to_representation(instance)

        # Agar product mavjud bo‘lsa — custom_title ni chiqarilmaydi
        if instance.product:
            rep['product'] = instance.product.id
            rep['product_title'] = instance.product.title
            rep.pop('custom_title', None)
        else:
            # Agar product yo‘q bo‘lsa — product chiqmasin
            rep.pop('product', None)
            rep.pop('product_title', None)

        return rep



class CartListSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = CartList
        fields = ['id', 'name', 'color', 'items']

    def create(self, validated_data):
        user = self.context['request'].user
        return CartList.objects.create(user=user, **validated_data)
