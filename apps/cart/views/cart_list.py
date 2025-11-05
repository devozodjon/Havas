from rest_framework import permissions, generics
from apps.cart.models import CartList
from apps.cart.serializers.cart_items import CartListSerializer


class CartListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = CartListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CartList.objects.filter(user=self.request.user)
