from django.urls import path

from finance.views import (
    AccountCreateView,
    AccountListView,
    AnalyticsView,
    CategoryCreateView,
    SignUpView,
    TransactionCreateView,
    TransactionDeleteView,
    TransactionUpdateView,
)

urlpatterns = [
    path("", AccountListView.as_view(), name="account_list"),
    path(
        "transactions/new/",
        TransactionCreateView.as_view(),
        name="transaction_create",
    ),
    path("signup/", SignUpView.as_view(), name="signup"),
    path("acconts/new/", AccountCreateView.as_view(), name="account_create"),
    path(
        "categories/new", CategoryCreateView.as_view(), name="category_create"
    ),
    path(
        "transactions/<int:pk>/edit/",
        TransactionUpdateView.as_view(),
        name="transaction_update",
    ),
    path(
        "transactions/<int:pk>/delete/",
        TransactionDeleteView.as_view(),
        name="transaction_delete",
    ),
    path("analytics/", AnalyticsView.as_view(), name="analytics"),
]
