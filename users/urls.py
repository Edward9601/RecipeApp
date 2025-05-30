from django.urls import path
from .views import UserRegistrationView, UserLoginView, guest_login, UserLogoutView


urlpatterns = [
    path('register', UserRegistrationView.as_view(), name='register'),
    path('', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('guest-login/', guest_login, name='guest_login'),
]