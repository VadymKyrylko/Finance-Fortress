from django import forms

from finance.models import Account, Category, Transaction


class TransactionForm(forms.ModelForm):
    category = forms.ModelChoiceField(
        queryset=Category.objects.none(),
        empty_label="Choose Category",
        required=False,
        label="Category",
    )

    class Meta:
        model = Transaction
        fields = (
            "type",
            "amount",
            "account",
            "category",
            "target_account",
            "description",
        )
        widgets = {
            "amount": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "0.00"}
            ),
            "account": forms.Select(attrs={"class": "form-select"}),
            "type": forms.Select(attrs={"class": "form-select"}),
            "category": forms.Select(attrs={"class": "form-select"}),
            "target_account": forms.Select(attrs={"class": "form-select"}),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": "3",
                    "placeholder": "Description",
                }
            ),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields["category"].queryset = Category.objects.filter(
                user=user
            )
            self.fields["account"].queryset = Account.objects.filter(user=user)
            self.fields["target_account"].queryset = Account.objects.filter(
                user=user
            )


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
