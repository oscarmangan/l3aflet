from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth.models import User


class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=250, help_text="Input a valid email address")

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2", )


class PasswordChange(PasswordChangeForm):

    class Meta:
        model = User
        fields = ("old_password", "new_password1", "new_password2", )
