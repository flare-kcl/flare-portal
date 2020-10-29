from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

app_name = "users"

# URLs that can be accessed by anyone
public_urlpatterns = [
    path("login/", auth_views.LoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
]

urlpatterns = [path("", views.user_list_view, name="user_list")]
