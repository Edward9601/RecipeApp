from django.shortcuts import redirect

class UsersAndGuestsAuth:
    """
    Mixin to check if the user is authenticated or a guest.
    """

    def dispatch(self, request, *args, **kwargs):
        session = request.session

        if request.user.is_authenticated or 'guest_id' in session:
            return super().dispatch(request, *args, **kwargs)
        return redirect('login')
          
            