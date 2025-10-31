from rest_framework import status
from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import AllowAny

from apps.products.models import ProductsModel
from apps.products.serializers.product_create import ProductCreateSerializer
from apps.shared.utils.custom_pagination import CustomPageNumberPagination
from apps.shared.utils.custom_response import CustomResponse


class ProductListCreateApiView(ListCreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = ProductCreateSerializer
    pagination_class = CustomPageNumberPagination


    def get_queryset(self):
        return ProductsModel.objects.filter(is_active=True)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            product = serializer.save()
            response_serializer = ProductCreateSerializer(product)
            return CustomResponse.success(
                message_key="SUCCESS_MESSAGE",
                data=response_serializer.data,
                status_code=status.HTTP_201_CREATED,
            )
        return CustomResponse.success(
            message_key="VALIDATION_ERROR",
            errors = serializer.errors
        )
