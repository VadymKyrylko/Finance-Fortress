from django.urls import path
from finance.views import AccountListView

urlpatterns = [
    path("", AccountListView.as_view(), name="account_list"),
]
