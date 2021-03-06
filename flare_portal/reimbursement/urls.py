from django.urls import path

from flare_portal.users.decorators import role_required
from flare_portal.utils.urls import decorate_urlpatterns

from . import views

app_name = "reimbursement"
urlpatterns = [
    path("vouchers/", views.voucher_pool_list_view, name="voucher_pool_list"),
    path("vouchers/add/", views.voucher_pool_create_view, name="voucher_pool_create"),
    path(
        "vouchers/<int:pk>/", views.voucher_pool_update_view, name="voucher_pool_update"
    ),
    path(
        "vouchers/<int:pk>/delete/",
        views.voucher_pool_delete_view,
        name="voucher_pool_delete",
    ),
    path(
        "vouchers/<int:pk>/upload/",
        views.voucher_upload_view,
        name="voucher_upload",
    ),
    path(
        "vouchers/<int:pk>/export/",
        views.voucher_export_view,
        name="voucher_export",
    ),
]
urlpatterns = decorate_urlpatterns(urlpatterns, role_required, "ADMIN")
