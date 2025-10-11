from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse

class LoginRequiredMiddleware:
    """
    Middleware that forces login for every view,
    except those you explicitly allow.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        # URLs you want to exclude from authentication check:
        self.exclude_paths = [
            reverse('login'),   # login page
            reverse('createUser')
        ]

    def __call__(self, request):
        # If user not authenticated and path not excluded → redirect
        if not request.user.is_authenticated and request.path not in self.exclude_paths:
            # return redirect('login')
            return JsonResponse({"login":"is required"})

        # Otherwise, continue normally
        response = self.get_response(request)
        return response
