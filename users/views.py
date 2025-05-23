from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserRegistrationForm



def register(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            return redirect('recipes/home')
    else:
        if request.user.is_authenticated:
            return redirect('recipes:home')
        form = UserRegistrationForm()

    return render(request, 'registration/register.html', {'form': form})
