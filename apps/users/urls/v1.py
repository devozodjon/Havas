from django.urls import path
from apps.users.views import RegisterView, LoginView, LogoutAPIView, ProfileRetrieveAPIView, VerifyEmailAPIView

app_name = 'users'
urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('verify-email/', VerifyEmailAPIView.as_view(), name='verify-email'),
    path("login/", LoginView.as_view(), name='login'),
    path('logout/', LogoutAPIView.as_view(), name='logout'),
    path('profile/', ProfileRetrieveAPIView.as_view(), name='profile'),

]

