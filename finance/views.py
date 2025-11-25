import calendar
from datetime import timedelta

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.db.models.functions import TruncDate
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import (
    CreateView,
    DeleteView,
    ListView,
    TemplateView,
    UpdateView,
)

from finance.forms import (
    AccountForm,
    AnalyticsFilterForm,
    CategoryForm,
    TransactionForm,
)
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
        kwargs["user"] = self.request.user
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


class AnalyticsView(LoginRequiredMixin, TemplateView):
    template_name = "finance/analytics.html"

    def get_date_ranges(self, comparison_type):
        """
        Returns a tuple: (start_current, end_current, start_prev, end_prev)
        """
        today = timezone.now().date()
        if comparison_type == "yoy_year":
            start_curr = today.replace(month=1, day=1)
            end_curr = today.replace(month=12, day=31)
            start_prev = start_curr.replace(year=start_curr.year - 1)
            end_prev = end_curr.replace(year=end_curr.year - 1)

        elif comparison_type == "yoy_month":
            start_curr = today.replace(day=1)
            last_day = calendar.monthrange(today.year, today.month)[1]
            end_curr = today.replace(day=last_day)

            start_prev = start_curr.replace(year=start_curr.year - 1)
            last_day_prev = calendar.monthrange(
                start_prev.year, start_prev.month
            )[1]
            end_prev = start_prev.replace(day=last_day_prev)

        else:
            start_curr = today.replace(day=1)
            last_day = calendar.monthrange(today.year, today.month)[1]
            end_curr = today.replace(day=last_day)

            first = today.replace(day=1)
            end_prev = first - timedelta(days=1)
            start_prev = end_prev.replace(day=1)

        return start_curr, end_curr, start_prev, end_prev

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = AnalyticsFilterForm(self.request.GET, user=self.request.user)
        comparison_type = self.request.GET.get("comparison_type", "mom")
        category_id = self.request.GET.get("category")

        start_curr, end_curr, _, _ = self.get_date_ranges(comparison_type)

        base_transactions = Transaction.objects.filter(
            user=self.request.user, date__range=(start_curr, end_curr)
        )
        income_transactions = base_transactions.filter(type="INCOME")
        expense_transactions = base_transactions.filter(type="EXPENSE")
        if category_id:
            expense_transactions = base_transactions.filter(
                category_id=category_id
            )

        # --- Chart (Income vs Expense vs Balance) ---
        total_income = (
            income_transactions.filter(type="INCOME").aggregate(Sum("amount"))[
                "amount__sum"
            ]
            or 0
        )
        total_expense = (
            expense_transactions.filter(type="EXPENSE").aggregate(
                Sum("amount")
            )["amount__sum"]
            or 0
        )
        total_balance = total_income - total_expense

        context["overview_chart_data"] = {
            "labels": ["Income", "Expenses", "Difference"],
            "data": [
                float(total_income),
                float(total_expense),
                float(total_balance),
            ],
            "colors": [
                "rgba(75, 192, 192, 0.7)",
                "rgba(255, 99, 132, 0.7)",
                "rgba(54, 162, 235, 0.7)",
            ],
        }

        # --- EXPENSES BY CATEGORIES ---
        expenses_by_cat = (
            expense_transactions.filter(type="EXPENSE")
            .values("category__name")
            .annotate(total=Sum("amount"))
            .order_by("-total")
        )

        cat_labels = []
        cat_data = []

        for entry in expenses_by_cat:
            cat_labels.append(entry["category__name"] or "Without category")
            cat_data.append(float(entry["total"]))

        context["category_chart_data"] = {
            "labels": cat_labels,
            "data": cat_data,
        }

        # --- DYNAMICS (Line Chart) ---
        income_dynamics = income_transactions.annotate(day=TruncDate("date")).values("day").annotate(total=Sum("amount")).order_by("day")

        expense_dynamics = (
            expense_transactions.annotate(day=TruncDate("date"))
            .values("day")
            .annotate(total=Sum("amount"))
            .order_by("day")
        )

        timeline = {}

        for entry in income_dynamics:
            day_str = entry["day"].strftime("%d.%m")

            if day_str not in timeline:
                timeline[day_str] = {"INCOME": 0, "EXPENSE": 0}
            timeline[day_str]["INCOME"] = float(entry["total"])

        for entry in expense_dynamics:
            day_str = entry["day"].strftime("%d.%m")
            if day_str not in timeline:
                timeline[day_str] = {"EXPENSE": 0, "INCOME": 0}
            timeline[day_str]["EXPENSE"] = float(entry["total"])

        dates_labels = sorted(list(timeline.keys()))
        income_series = [timeline[d]["INCOME"] for d in dates_labels]
        expense_series = [timeline[d]["EXPENSE"] for d in dates_labels]

        context["dynamics_chart_data"] = {
            "labels": dates_labels,
            "income": income_series,
            "expense": expense_series,
        }

        # --- FINAL CONTEXT ---
        context["form"] = form
        context["period_label"] = (
            f"{start_curr.strftime('%d.%m.%Y')}"
            f" - {end_curr.strftime('%d.%m.%Y')}"
        )

        return context
