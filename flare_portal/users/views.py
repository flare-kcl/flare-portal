from typing import Any

from django import forms
from django.contrib import messages
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView

from .forms import UserCreateForm, UserUpdateForm
from .models import User


class UserListView(ListView):
    context_object_name = "users"

    def get_queryset(self) -> QuerySet:
        return User.objects.order_by("first_name")


user_list_view = UserListView.as_view()


class UserCreateView(CreateView):
    form_class = UserCreateForm
    success_url = reverse_lazy("users:user_list")
    template_name = "users/user_create_form.html"
    object = None

    def form_valid(self, form: forms.BaseModelForm) -> HttpResponse:
        response = super().form_valid(form)
        messages.success(self.request, f'Added new user "{self.object}"')
        return response


user_create_view = UserCreateView.as_view()


class UserUpdateView(UpdateView):
    form_class = UserUpdateForm
    model = User
    success_url = reverse_lazy("users:user_list")
    object = None

    def form_valid(self, form: forms.BaseModelForm) -> HttpResponse:
        response = super().form_valid(form)
        messages.success(self.request, f'Updated user "{self.object}"')
        return response


user_update_view = UserUpdateView.as_view()


class UserDeleteView(DeleteView):
    context_object_name = "user"
    model = User
    success_url = reverse_lazy("users:user_list")

    def delete(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        user = self.get_object()
        response = super().delete(request, *args, **kwargs)
        messages.success(self.request, f'Deleted user "{user}"')
        return response


user_delete_view = UserDeleteView.as_view()
