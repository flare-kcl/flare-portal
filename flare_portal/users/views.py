from django.contrib.auth import get_user_model
from django.views.generic.list import ListView

User = get_user_model()


class UserListView(ListView):
    model = User
    context_object_name = "users"


user_list_view = UserListView.as_view()
