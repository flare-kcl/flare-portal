from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

app_name = "users"

# URLs that can be accessed by anyone
# These are referenced in the main urls.py file
public_urlpatterns = [
    path("login/", auth_views.LoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
]

urlpatterns = [
    path("users/", views.user_list_view, name="user_list"),
    path("users/add/", views.user_create_view, name="user_create"),
    path("users/<int:pk>/edit/", views.user_update_view, name="user_update"),
    path("users/<int:pk>/delete/", views.user_delete_view, name="user_delete"),
]
