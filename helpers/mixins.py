from django.shortcuts import redirect
from django.contrib import messages

class RegisteredUserAuthRequired:
    """
    Mixin to check if the user is authenticated and not authenticated as a guest.
    """

    def dispatch(self, request, *args, **kwargs):

        if request.user.is_authenticated and not request.user.username.startswith('guest'):
            # If the user is authenticated and not a guest, proceed with the request
            return super().dispatch(request, *args, **kwargs)
        referer = request.META.get('HTTP_REFERER')
        messages.warning(request, "You must be a registered user to access this page. " \
        "Please register or log in.")
        # Redirect to the referer if available, otherwise redirect to login page
        if referer:
            return redirect(referer)
        return redirect('login')
          
            