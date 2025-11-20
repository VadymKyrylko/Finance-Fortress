from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from datetime import date


def get_first_day_of_current_month():
    today = timezone.now().date()
    return date(today.year, today.month, 1)


# ==========================
# Core & Settings Models
# ==========================
class Tag(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Category(models.Model):
    class CategoryType(models.TextChoices):
        INCOME = "INCOME", "INCOME"
        EXPENSE = "EXPENSE", "EXPENSE"

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="categories"
    )
    name = models.CharField(max_length=100)
    type = models.CharField(
        max_length=10,
        choices=CategoryType.choices,
        default=CategoryType.EXPENSE,
    )
    icon = models.CharField(max_length=50, blank=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return f"{self.name} ({self.type})"


class ExchangeRate(models.Model):
    class CurrencyChoices(models.TextChoices):
        USD = "USD", "US Dollar"
        EUR = "EUR", "Euro"

    currency = models.CharField(max_length=3, choices=CurrencyChoices)
    rate = models.DecimalField(max_digits=8, decimal_places=4)
    date = models.DateField(default=timezone.now)

    class Meta:
        unique_together = ("currency", "date")
        ordering = [
            "-date",
        ]


# ==========================
# Main Finance Models
# ==========================
class Account(models.Model):
    class CurrencyChoices(models.TextChoices):
        USD = "USD", "US Dollar"
        EUR = "EUR", "Euro"
        UAH = "UAH", "Ukrainian Hryvnia"

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="accounts"
    )
    name = models.CharField(max_length=100)
    currency = models.CharField(
        max_length=3,
        choices=CurrencyChoices.choices,
        default=CurrencyChoices.UAH,
    )
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    include_in_total = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.currency})"


class Transaction(models.Model):
    class TransactionType(models.TextChoices):
        INCOME = "INCOME", "INCOME"
        EXPENSE = "EXPENSE", "EXPENSE"
        TRANSFER = "TRANSFER", "TRANSFER"

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    account = models.ForeignKey(
        Account, on_delete=models.CASCADE, related_name="transactions"
    )
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True
    )
    target_account = models.ForeignKey(
        Account,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transfers_in",
    )
    tags = models.ManyToManyField(Tag, blank=True)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    type = models.CharField(max_length=10, choices=TransactionType.choices)
    date = models.DateTimeField(default=timezone.now)
    description = models.TextField(blank=True)

    class Meta:
        ordering = [
            "-date",
        ]


# ==========================
# Analytics & Limits
# ==========================
class Budget(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="budgets"
    )
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    amount_limit = models.DecimalField(max_digits=15, decimal_places=2)
    month = models.DateField(default=get_first_day_of_current_month)

    class Meta:
        unique_together = ("user", "category", "month")

    def __str__(self):
        return f"{self.category} - {self.month}"
