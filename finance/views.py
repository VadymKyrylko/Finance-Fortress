from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, DeleteView

from finance.forms import AccountForm, CategoryForm, TransactionForm
from finance.models import Account, Category, Transaction


class AccountListView(LoginRequiredMixin, ListView):
    model = Account
    template_name = "finance/account_list.html"
    context_object_name = "accounts"

    def get_queryset(self):
        return Account.objects.filter(user=self.request.user).order_by("name")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["transactions"] = (
            Transaction.objects.filter(user=self.request.user)
            .select_related("category", "account", "target_account")
            .order_by("-date")[:10]
        )
        return context


class TransactionCreateView(LoginRequiredMixin, CreateView):
    model = Transaction
    form_class = TransactionForm
    template_name = "finance/transaction_form.html"
    success_url = reverse_lazy("account_list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class SignUpView(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"


class AccountCreateView(LoginRequiredMixin, CreateView):
    model = Account
    form_class = AccountForm
    template_name = "finance/form_base.html"
    success_url = reverse_lazy("account_list")

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Create new Account"
        context["btn_text"] = "Create Account"
        return context


class CategoryCreateView(LoginRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = "finance/form_base.html"
    success_url = reverse_lazy("account_list")

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Create new Category"
        context["btn_text"] = "Create Category"
        return context


class TransactionUpdateView(LoginRequiredMixin, UpdateView):
    model = Transaction
    form_class = TransactionForm
    template_name = "finance/form_base.html"
    success_url = reverse_lazy("account_list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Update Transaction"
        context["btn_text"] = "Update Transaction"
        return context

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)


class TransactionDeleteView(LoginRequiredMixin, DeleteView):
    model = Transaction
    template_name = "finance/transaction_confirm_delete.html"
    success_url = reverse_lazy("account_list")

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)
