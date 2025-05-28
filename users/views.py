from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout
from django.urls import reverse_lazy
from .forms import UserRegistrationForm, LoginForm
from django.views.generic import CreateView, View
from django.contrib.auth.views import LogoutView, LoginView

class UserRegistrationView(CreateView):
    """
    View to handle user registration
    """
    form_class = UserRegistrationForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('recipes:home') 


    def form_valid(self, form):
        response = super().form_valid(form)
        username = form.cleaned_data.get('username')
        messages.success(self.request, f'Account created for {username}!')
        return response
    

class UserLoginView(LoginView):
    """
    View to handle user login
    """
    form_class = LoginForm
    template_name = 'registration/login.html'
    success_url = reverse_lazy('recipes:home')

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        form = self.form_class(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect(self.success_url)
        return render(request, self.template_name, {'form': form})


class UserLogoutView(LogoutView):
    """
    View to handle user logout
    """
    next_page = 'login'
    
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

