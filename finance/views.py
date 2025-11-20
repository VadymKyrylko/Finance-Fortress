from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic import ListView
from finance.models import Account


class AccountListView(LoginRequiredMixin, ListView):
    model = Account
    template_name = "finance/account_list.html"
    context_object_name = "accounts"

    def get_queryset(self):
        return Account.objects.filter(user=self.request.user).order_by("name")
