from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_GET,require_POST
from core.models.Exams_models import Exam, Subject
from ..services.forms_depricated.createAccount import SignUpForm
from django.contrib.auth import login

# create Account

def signup_view(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)   # auto login after registration
            return redirect("home")  # change "home" to your homepage url name
    else:
        form = SignUpForm()
    return render(request, "registration/signup.html", {"form": form})
# create Year
# create subject
# create Question Bank
# create Exam