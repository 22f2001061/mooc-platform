from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect, render


def signup(request):
    """
    User registration using Django's built-in UserCreationForm.
    On success, auto-login and redirect to course list.
    """
    if request.user.is_authenticated:
        return redirect("courses:list")

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("courses:list")
    else:
        form = UserCreationForm()

    return render(request, "accounts/signup.html", {"form": form})
