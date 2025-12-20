from django.http import JsonResponse,HttpRequest
from django.shortcuts import redirect

from django.urls import reverse
import logging
import uuid
logger = logging.getLogger("django")
class LoginRequiredMiddleware:
    """
    Middleware that forces login for every view,
    except those you explicitly allow.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        # URLs you want to exclude from authentication check:
        self.exclude_paths = [
            reverse('API_v0_login'),
            reverse('API_v0_createUser')
        ]

    def __call__(self, request:HttpRequest):
        try:
            # If user not authenticated and path not excluded → redirect
            if not request.user.is_authenticated and request.path not in self.exclude_paths:
                if request.path.startswith("/api"):
                    return JsonResponse({"login":"is required"},status=403) 
                return redirect('userloginPage')
            # Otherwise, continue normally
            response = self.get_response(request)
            return response
        #------------------
        except Exception as e:
            errorID = uuid.uuid4().hex[:5]
            user_id = getattr(request.user, "id", None)
            user_label = user_id if user_id is not None else "AnonymousUser"
            logger.exception(
                f"Request-Path:{request.path};\n"
                f"User-ID:{user_label};\n"
                f"ERR-ID:{errorID}\n"
                f"{'-'*100}"
            )
            userError = f"unexpected error ERR-ID:{errorID}"
            return JsonResponse({"fail":userError},status=500)
        #------------------
