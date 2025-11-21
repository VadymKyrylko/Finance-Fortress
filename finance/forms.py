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
