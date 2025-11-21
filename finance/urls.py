from django.urls import path

from finance.views import AccountListView, SignUpView, TransactionCreateView

urlpatterns = [
    path("", AccountListView.as_view(), name="account_list"),
    path("new/", TransactionCreateView.as_view(), name="transaction_create"),
    path("signup/", SignUpView.as_view(), name="signup"),
]
