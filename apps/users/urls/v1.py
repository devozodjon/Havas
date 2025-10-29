from django.urls import path

from apps.users.views.device import DeviceRegisterCreateAPIView, DeviceListApiView

app_name = 'users'

urlpatterns = [
    path('devices/', DeviceRegisterCreateAPIView.as_view(), name='device-register'),
    path('devices/list/', DeviceListApiView.as_view(), name='device-list'),
]
