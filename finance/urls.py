from django.urls import path

from finance.views import AccountListView, TransactionCreateView

urlpatterns = [
    path("", AccountListView.as_view(), name="account_list"),
    path("new/", TransactionCreateView.as_view(), name="transaction_create"),
]
