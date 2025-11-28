from decimal import Decimal

import factory
from django.contrib.auth.models import User

from finance.models import Account, Budget, Category, Tag, Transaction


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"test_user_{n}")
    email = factory.Sequence(lambda n: f"user{n}@example.com")


class AccountFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Account

    user = factory.SubFactory(UserFactory)
    name = "Test Account"
    balance = Decimal("1000.00")
    currency = "UAH"


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category

    user = factory.SubFactory(UserFactory)
    name = "Test Category"
    type = "EXPENSE"


class TransactionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Transaction

    user = factory.SubFactory(UserFactory)
    account = factory.SubFactory(AccountFactory)
    category = factory.SubFactory(CategoryFactory)
    amount = Decimal("100.00")
    type = "EXPENSE"
    description = "Test Transaction"


class TagFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Tag

    user = factory.SubFactory(UserFactory)
    name = "Test Tag"


class BudgetFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Budget

    user = factory.SubFactory(UserFactory)
    category = factory.SubFactory(CategoryFactory)
    amount_limit = Decimal("1000.00")
