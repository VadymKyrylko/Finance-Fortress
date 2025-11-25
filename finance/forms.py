from django import forms
from django.core.exceptions import ValidationError

from finance.models import Account, Category, Transaction


class ExpenseForm(forms.ModelForm):
    force_overdraft = forms.BooleanField(
        required=False,
        label="Allow negative balance",
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )

    class Meta:
        model = Transaction
        fields = ["account", "category", "amount", "date", "description"]
        widgets = {
            "date": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
            "amount": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "0.00"}
            ),
            "description": forms.Textarea(
                attrs={"class": "form-control", "rows": "2"}
            ),
            "account": forms.Select(attrs={"class": "form-select"}),
            "category": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields["account"].queryset = Account.objects.filter(user=user)
            self.fields["category"].queryset = Category.objects.filter(
                user=user, type="EXPENSE"
            )

    def clean(self):
        cleaned_data = super().clean()
        account = self.cleaned_data.get("account")
        amount = self.cleaned_data.get("amount")
        force_overdraft = self.cleaned_data.get("force_overdraft")

        if account and amount:
            if account.balance < amount and not force_overdraft:
                raise ValidationError(
                    f"Not enough balance on {account.name} "
                    f"({account.balance}). Check the box "
                    f"'Allow negative balance' if you want to continue anyway."
                )
        return cleaned_data


class IncomeForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ["account", "category", "amount", "date", "description"]
        widgets = {
            "date": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
            "amount": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "0.00"}
            ),
            "description": forms.Textarea(
                attrs={"class": "form-control", "rows": "2"}
            ),
            "account": forms.Select(attrs={"class": "form-select"}),
            "category": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields["account"].queryset = Account.objects.filter(user=user)
            self.fields["category"].queryset = Category.objects.filter(
                user=user, type="INCOME"
            )


class TransferForm(forms.ModelForm):
    force_overdraft = forms.BooleanField(
        required=False,
        label="Allow negative balance",
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )

    class Meta:
        model = Transaction
        fields = ["account", "target_account", "amount", "date", "description"]
        widgets = {
            "date": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
            "amount": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "0.00"}
            ),
            "description": forms.Textarea(
                attrs={"class": "form-control", "rows": "2"}
            ),
            "account": forms.Select(
                attrs={"class": "form-select", "label": "From account"}
            ),
            "target_account": forms.Select(
                attrs={"class": "form-select", "label": "To account"}
            ),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields["account"].queryset = Account.objects.filter(user=user)
            self.fields["target_account"].queryset = Account.objects.filter(
                user=user
            )

    def clean(self):
        cleaned_data = super().clean()
        account = cleaned_data.get("account")
        target_account = cleaned_data.get("target_account")
        amount = self.cleaned_data.get("amount")
        force_overdraft = self.cleaned_data.get("force_overdraft")

        if account == target_account:
            raise ValidationError(
                "You can't make a transfer to the same account."
            )
        if account and amount:
            if account.balance < amount and not force_overdraft:
                raise ValidationError(
                    f"Not enough balance on {account.name} "
                    f"({account.balance}). Check the box "
                    f"'Allow negative balance' if you want to continue anyway."
                )
        return cleaned_data


class AccountForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ("name", "currency", "balance", "include_in_total")
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Name (eg. Cash)",
                }
            ),
            "currency": forms.Select(attrs={"class": "form-select"}),
            "balance": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "0.00"}
            ),
            "include_in_total": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
        }


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ("name", "type", "icon")
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Name(eg. Food"}
            ),
            "type": forms.Select(attrs={"class": "form-select"}),
            "icon": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Bootstrap icon class (eg. bi-cart)",
                }
            ),
        }


class AnalyticsFilterForm(forms.Form):
    TIME_RANGE_CHOICES = [
        ("mom", "current month to previous month"),
        ("yoy_month", "current month to same month last year"),
        ("yoy_year", "current year to previous year"),
    ]

    comparison_type = forms.ChoiceField(
        choices=TIME_RANGE_CHOICES,
        required=False,
        label="Comparison Period",
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    category = forms.ModelChoiceField(
        queryset=Category.objects.none(),
        required=False,
        label="Category",
        empty_label="All Categories",
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields["category"].queryset = Category.objects.filter(
                user=user
            )
