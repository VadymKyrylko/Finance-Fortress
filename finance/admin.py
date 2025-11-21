from django.contrib import admin

from finance.models import (
    Account,
    Budget,
    Category,
    ExchangeRate,
    Tag,
    Transaction,
)


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ("name", "balance", "currency", "user")
    list_filter = ("user", "currency")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "type", "user")
    list_filter = ("type", "user")


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("user", "type", "amount", "account", "category", "date")
    list_filter = ("type", "date", "user")
    date_hierarchy = "date"


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ("user", "category", "amount_limit", "month")


admin.site.register(ExchangeRate)
admin.site.register(Tag)
