from django.shortcuts import redirect
from django.contrib import messages

from utils.helpers.constants import GUEST_USER_NAME


class RegisteredUserAuthRequired:
    """
    Mixin to check if the user is authenticated and not authenticated as a guest.
    """

    def dispatch(self, request, *args, **kwargs):
        # If the user is not authenticated,should exit early and redirect to login page
        if not request.user.is_authenticated:
            return redirect('login')
        if request.user.username == GUEST_USER_NAME:
            referer = request.META.get('HTTP_REFERER')
            messages.warning(request, "You must be a registered user to access this page. "
                                      "Please register or log in.")
            # Redirect to the referer if available, otherwise redirect to login page
            if referer:
                return redirect(referer)
            else:
                return redirect('login')
        # If the user is authenticated and not a guest, proceed with the request
        return super().dispatch(request, *args, **kwargs)
