from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.views.generic.list import ListView

from .forms import UserCreateForm

User = get_user_model()


class UserListView(ListView):
    model = User
    context_object_name = "users"


user_list_view = UserListView.as_view()


class UserCreateView(CreateView):
    form_class = UserCreateForm
    success_url = reverse_lazy("users:user_list")
    template_name = "users/user_create_form.html"


user_create_view = UserCreateView.as_view()
