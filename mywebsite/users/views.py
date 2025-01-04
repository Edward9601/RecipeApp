from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserRegistrationForm


# Create your views here.
def register(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            return redirect('recipes/home')
    else:
        form = UserRegistrationForm()

    # Ensure the form is rendered regardless of the request method or form validity
    return render(request, 'registration/register.html', {'form': form})
