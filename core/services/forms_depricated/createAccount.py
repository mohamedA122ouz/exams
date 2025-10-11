from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class SignUpForm(UserCreationForm):
    attribute = "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-600 dark:border-gray-500 dark:placeholder-gray-400 dark:text-white"
    # email = forms.EmailField(widget=forms.TextInputattrs={
    #     "class":attribute,
    #     "type":"email"
    # })

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
