from django.urls import path

from finance.views import (
    AccountCreateView,
    AccountListView,
    AnalyticsView,
    CategoryCreateView,
    CategoryDeleteView,
    CategoryListView,
    CategoryUpdateView,
    ExpenseCreateView,
    IncomeCreateView,
    SignUpView,
    TransactionDeleteView,
    TransactionUpdateView,
    TransferCreateView,
)

urlpatterns = [
    path("", AccountListView.as_view(), name="account_list"),
    path(
        "transactions/income/",
        IncomeCreateView.as_view(),
        name="income_create",
    ),
    path(
        "transactions/expense/",
        ExpenseCreateView.as_view(),
        name="expense_create",
    ),
    path(
        "transactions/transfer/",
        TransferCreateView.as_view(),
        name="transfer_create",
    ),
    path("signup/", SignUpView.as_view(), name="signup"),
    path("acconts/new/", AccountCreateView.as_view(), name="account_create"),
    path(
        "categories/new", CategoryCreateView.as_view(), name="category_create"
    ),
    path("categories/", CategoryListView.as_view(), name="category_list"),
    path(
        "categories/<int:pk>/edit/",
        CategoryUpdateView.as_view(),
        name="category_update",
    ),
    path(
        "categories/<int:pk>/delete",
        CategoryDeleteView.as_view(),
        name="category_delete",
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
