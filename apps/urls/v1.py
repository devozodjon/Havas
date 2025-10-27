from django.urls import path, include

urlpatterns = [
    path('users/', include('apps.users.urls.v1')),
    path('shared/', include('apps.shared.urls.v1')),
    path('cart/', include('apps.cart.urls.v1')),
    path('products/', include('apps.products.urls.v1')),
    path('recipes/', include('apps.recipes.urls.v1')),
    path('history/', include('apps.history.urls.v1')),

]
