from django.urls import path
from .views import UserRegistrationView, UserLoginView
from django.contrib.auth.views import LogoutView


urlpatterns = [
    path('', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
]