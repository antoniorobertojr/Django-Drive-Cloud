from django.urls import path

from .views import LoginView, SignupView, TestTokenView

urlpatterns = [
    path("signup/", SignupView.as_view(), name="signup"),
    path("login/", LoginView.as_view(), name="login"),
    path("test-token/", TestTokenView.as_view(), name="test-token"),
]
