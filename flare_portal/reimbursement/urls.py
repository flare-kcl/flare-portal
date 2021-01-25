from django.urls import path

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
]
