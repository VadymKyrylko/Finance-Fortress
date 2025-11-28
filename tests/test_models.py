from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from finance.models import (
    Account,
    Budget,
    Category,
    Tag,
    Transaction,
    get_first_day_of_current_month,
)
from tests.factories import (
    AccountFactory,
    BudgetFactory,
    CategoryFactory,
    TagFactory,
    TransactionFactory,
    UserFactory,
)


# ====================================================
# --- STR REPRESENTATION ---
# ====================================================
@pytest.mark.django_db
def test_account_str_method():
    """Check Account string representation"""
    account = AccountFactory(name="Monobank", currency="UAH")
    assert str(account) == "Monobank (UAH)"


@pytest.mark.django_db
def test_category_str_method():
    """Check Category string representation"""
    category = CategoryFactory(name="Food", type="EXPENSE")
    assert str(category) == "Food (EXPENSE)"


@pytest.mark.django_db
def test_tag_str_method():
    """Check Tag string representation"""
    user = UserFactory()
    tag = TagFactory(user=user, name="Tag_name")
    assert str(tag) == "Tag_name"


@pytest.mark.django_db
def test_budget_str_method():
    """Check Budget string representation"""
    user = UserFactory()
    category = CategoryFactory(user=user, name="Food")
    budget = BudgetFactory(user=user, category=category)
    assert str(budget) == f"{category} - {budget.month}"


# ====================================================
# --- TRANSACTIONS ---
# ====================================================
@pytest.mark.django_db
def test_transaction_has_valid_data():
    """Check that Transaction stores valid data correctly."""
    user = UserFactory()
    income_category = CategoryFactory(type="INCOME")
    expense_category = CategoryFactory(type="EXPENSE")
    acc1 = AccountFactory(
        user=user,
        name="Cash",
        balance=Decimal("1000.00"),
    )
    acc2 = AccountFactory(user=user, balance=Decimal("0.00"), name="Mono")
    tr_income = TransactionFactory(
        user=user,
        account=acc1,
        type="INCOME",
        category=income_category,
        amount=Decimal("1000.00"),
    )
    tr_expense = TransactionFactory(
        user=user,
        account=acc1,
        type="EXPENSE",
        category=expense_category,
        amount=Decimal("500.00"),
    )
    tr_transfer = TransactionFactory(
        user=user,
        account=acc1,
        type="TRANSFER",
        target_account=acc2,
        amount=Decimal("500.00"),
    )
    assert tr_income.amount == Decimal("1000.00")
    assert tr_expense.amount == Decimal("500.00")
    assert tr_transfer.amount == Decimal("500.00")
    assert tr_income.type == "INCOME"
    assert tr_expense.type == "EXPENSE"
    assert tr_transfer.type == "TRANSFER"
    assert tr_income.category == income_category
    assert tr_expense.category == expense_category
    assert tr_transfer.account == acc1
    assert tr_transfer.target_account == acc2


# ====================================================
# --- ACCOUNTS ---
# ====================================================
@pytest.mark.django_db
def test_accounts_has_valid_data():
    """Check that Account stores valid data correctly."""
    user = UserFactory()
    account = AccountFactory(
        user=user,
        balance=Decimal("1000.00"),
        name="Cash",
        currency="USD",
        include_in_total=False,
    )
    assert account.balance == Decimal("1000.00")
    assert account.name == "Cash"
    assert account.currency == "USD"
    assert account.user == user
    assert account.include_in_total is False


@pytest.mark.django_db
def test_account_rounds_up_more_than_2_decimal_places():
    """Check that balance rounds up (e.g. 1000.555 -> 1000.56)."""
    user = UserFactory()
    account = AccountFactory(
        user=user,
        balance=Decimal("1000.555"),
        name="Cash",
    )
    account.refresh_from_db()
    assert account.balance == Decimal("1000.56")


@pytest.mark.django_db
def test_account_rounds_down_more_than_2_decimal_places():
    """Check that balance rounds down (e.g. 1000.554 -> 1000.55)."""
    user = UserFactory()
    account = AccountFactory(
        user=user,
        balance=Decimal("1000.554"),
        name="Cash",
    )
    account.refresh_from_db()
    assert account.balance == Decimal("1000.55")


@pytest.mark.django_db
def test_account_has_invalid_currency():
    """Check validation for invalid currency code."""
    user = UserFactory()
    account = AccountFactory.build(currency="USDDDDD")
    with pytest.raises(ValidationError):
        account.full_clean()


@pytest.mark.django_db
def test_account_has_invalid_name():
    """Check validation for too long account name."""
    user = UserFactory()
    long_name = "A" * 101
    account = AccountFactory.build(name=long_name)
    with pytest.raises(ValidationError):
        account.full_clean()


@pytest.mark.django_db
def test_account_has_not_user():
    """Check IntegrityError when creating Account without user."""
    with pytest.raises(IntegrityError):
        AccountFactory.create(user=None)


@pytest.mark.django_db
def test_account_has_invalid_balance():
    """Check validation for balance exceeding max digits."""
    big_number = "1" * 16 + ".00"
    account = AccountFactory.build(
        balance=Decimal(big_number),
    )
    with pytest.raises(ValidationError):
        account.full_clean()


# ====================================================
# --- INCOME ACCOUNTS ---
# ====================================================
@pytest.mark.django_db
def test_income_increases_balance():
    """Check that creating INCOME transaction increases balance."""
    account = AccountFactory(balance=Decimal("0.00"))
    TransactionFactory(
        user=account.user,
        account=account,
        type="INCOME",
        amount=Decimal("500.00"),
    )
    account.refresh_from_db()
    assert account.balance == Decimal("500.00")


@pytest.mark.django_db
def test_zero_income_not_allowed():
    """Check validation preventing zero amount in INCOME."""
    transaction = TransactionFactory.build(
        type="INCOME", amount=Decimal("0.00")
    )
    with pytest.raises(ValidationError):
        transaction.full_clean()


@pytest.mark.django_db
def test_negative_income_not_allowed():
    """Check validation preventing negative amount in INCOME."""
    transaction = TransactionFactory.build(
        type="INCOME", amount=Decimal("-500.00")
    )
    with pytest.raises(ValidationError):
        transaction.full_clean()


@pytest.mark.django_db
def test_overflow_income_not_allowed():
    """Check validation for INCOME amount exceeding max digits."""
    big_number = "1" * 16 + ".00"
    transaction = TransactionFactory.build(
        type="INCOME",
        amount=Decimal(big_number),
    )
    with pytest.raises(ValidationError):
        transaction.full_clean()


# ====================================================
# --- EXPENSE ACCOUNTS ---
# ====================================================
@pytest.mark.django_db
def test_expense_decreases_balance():
    """Check that creating EXPENSE transaction decreases balance."""
    account = AccountFactory(balance=Decimal("1000.00"))
    TransactionFactory(
        user=account.user,
        account=account,
        type="EXPENSE",
        amount=Decimal("300.00"),
    )
    account.refresh_from_db()
    assert account.balance == Decimal("700.00")


@pytest.mark.django_db
def test_delete_expense_restores_balance():
    """Check that deleting EXPENSE restores balance."""
    account = AccountFactory(balance=Decimal("1000.00"))
    transaction = TransactionFactory(
        user=account.user,
        account=account,
        type="EXPENSE",
        amount=Decimal("200.00"),
    )
    account.refresh_from_db()
    assert account.balance == Decimal("800.00")
    transaction.delete()
    account.refresh_from_db()
    assert account.balance == Decimal("1000.00")


@pytest.mark.django_db
def test_update_expense_amount_changes_balance():
    """Check that updating EXPENSE amount recalculates balance correctly."""
    acc = AccountFactory(balance=Decimal("1000.00"))
    transaction = TransactionFactory(
        account=acc, type="EXPENSE", amount=Decimal("100.00")
    )
    transaction.amount = Decimal("300.00")
    transaction.save()
    acc.refresh_from_db()
    assert acc.balance == Decimal("700.00")


@pytest.mark.django_db
def test_update_expense_account_moves_balance():
    """Check balance changes when moving EXPENSE to another account."""
    user = UserFactory()
    acc1 = AccountFactory(user=user, balance=Decimal("1000.00"))
    acc2 = AccountFactory(user=user, balance=Decimal("1000.00"))
    transaction = TransactionFactory(
        account=acc1, type="EXPENSE", amount=Decimal("100.00")
    )
    transaction.account = acc2
    transaction.save()
    acc1.refresh_from_db()
    acc2.refresh_from_db()
    assert acc1.balance == Decimal("1000.00")
    assert acc2.balance == Decimal("900.00")


@pytest.mark.django_db
def test_zero_expense_not_allowed():
    """Check validation preventing zero amount in EXPENSE."""
    transaction = TransactionFactory.build(
        type="EXPENSE", amount=Decimal("0.00")
    )
    with pytest.raises(ValidationError):
        transaction.full_clean()


@pytest.mark.django_db
def test_negative_expense_not_allowed():
    """Check validation preventing negative amount in EXPENSE."""
    transaction = TransactionFactory.build(
        type="EXPENSE", amount=Decimal("-500.00")
    )
    with pytest.raises(ValidationError):
        transaction.full_clean()


@pytest.mark.django_db
def test_overflow_expense_not_allowed():
    """Check validation for EXPENSE amount exceeding max digits."""
    big_number = "1" * 16 + ".00"
    transaction = TransactionFactory.build(
        type="EXPENSE",
        amount=Decimal(big_number),
    )
    with pytest.raises(ValidationError):
        transaction.full_clean()


# ====================================================
# --- TRANSFER ACCOUNTS ---
# ====================================================
@pytest.mark.django_db
def test_transfer_updates_both_accounts():
    """Check that creating TRANSFER updates both balances correctly."""
    user = UserFactory()
    source_acc = AccountFactory(user=user, balance=Decimal("1000.00"))
    target_acc = AccountFactory(user=user, balance=Decimal("0.00"))
    TransactionFactory(
        user=user,
        account=source_acc,
        target_account=target_acc,
        type="TRANSFER",
        amount=Decimal("300.00"),
    )
    source_acc.refresh_from_db()
    target_acc.refresh_from_db()
    assert source_acc.balance == Decimal("700.00")
    assert target_acc.balance == Decimal("300.00")


@pytest.mark.django_db
def test_delete_transfer_restores_both_accounts():
    """Check that deleting TRANSFER restores balances on both accounts."""
    user = UserFactory()
    source_acc = AccountFactory(user=user, balance=Decimal("1000.00"))
    target_acc = AccountFactory(user=user, balance=Decimal("0.00"))
    transaction = TransactionFactory(
        user=user,
        account=source_acc,
        target_account=target_acc,
        type="TRANSFER",
        amount=Decimal("300.00"),
    )
    transaction.delete()
    source_acc.refresh_from_db()
    target_acc.refresh_from_db()
    assert source_acc.balance == Decimal("1000.00")
    assert target_acc.balance == Decimal("0.00")


@pytest.mark.django_db
def test_update_transfer_target_account():
    """Check balance changes when updating target account of TRANSFER."""
    user = UserFactory()
    acc_a = AccountFactory(user=user, balance=Decimal("1000.00"))
    acc_b = AccountFactory(user=user, balance=Decimal("0.00"))
    acc_c = AccountFactory(user=user, balance=Decimal("0.00"))
    transaction = TransactionFactory(
        user=user,
        account=acc_a,
        target_account=acc_b,
        type="TRANSFER",
        amount=Decimal("300.00"),
    )
    transaction.target_account = acc_c
    transaction.save()
    acc_a.refresh_from_db()
    acc_b.refresh_from_db()
    acc_c.refresh_from_db()
    assert acc_a.balance == Decimal("700.00")
    assert acc_b.balance == Decimal("0.00")
    assert acc_c.balance == Decimal("300.00")


@pytest.mark.django_db
def test_zero_transfer_not_allowed():
    """Check validation preventing zero amount in TRANSFER."""
    transaction = TransactionFactory.build(
        type="TRANSFER", amount=Decimal("0.00")
    )
    with pytest.raises(ValidationError):
        transaction.full_clean()


@pytest.mark.django_db
def test_negative_transfer_not_allowed():
    """Check validation preventing negative amount in TRANSFER."""
    user = UserFactory()
    target_acc = AccountFactory(user=user, balance=Decimal("0.00"))
    transaction = TransactionFactory.build(
        type="TRANSFER", target_account=target_acc, amount=Decimal("-500.00")
    )
    with pytest.raises(ValidationError):
        transaction.full_clean()


@pytest.mark.django_db
def test_overflow_transfer_not_allowed():
    """Check validation for TRANSFER amount exceeding max digits."""
    user = UserFactory()
    acc_b = AccountFactory(user=user, balance=Decimal("0.00"))
    big_number = "1" * 16 + ".00"
    transaction = TransactionFactory.build(
        type="TRANSFER",
        amount=Decimal(big_number),
        target_account=acc_b,
    )
    with pytest.raises(ValidationError):
        transaction.full_clean()


# ====================================================
# --- USER ---
# ====================================================
@pytest.mark.django_db
def test_cascade_delete_user_deletes_all_related_objects():
    """Check that deleting User cascades to all related objects."""
    user = UserFactory()
    account = AccountFactory(user=user)
    category = CategoryFactory(name="Food", type="EXPENSE", user=user)
    transaction = TransactionFactory(
        user=user, account=account, category=category
    )
    tag = TagFactory(user=user, name="Tag_name")
    budget = BudgetFactory(
        user=user, category=category, month=get_first_day_of_current_month()
    )
    assert Transaction.objects.count() == 1
    assert Account.objects.count() == 1
    assert Category.objects.count() == 1
    assert Tag.objects.count() == 1
    assert Budget.objects.count() == 1
    user.delete()
    assert Transaction.objects.count() == 0
    assert Account.objects.count() == 0
    assert Category.objects.count() == 0
    assert Tag.objects.count() == 0
    assert Budget.objects.count() == 0


# ====================================================
# --- CATEGORIES ---
# ====================================================
@pytest.mark.django_db
def test_category_data_is_valid():
    """Check that Category stores valid data correctly."""
    category = CategoryFactory(name="Food", type="EXPENSE")
    assert Category.objects.count() == 1
    assert Category.objects.first().name == "Food"
    assert Category.objects.first().type == "EXPENSE"
    assert Category.objects.first().user == category.user


@pytest.mark.django_db
def test_category_name_is_too_long():
    """Check validation for too long Category name."""
    user = UserFactory()
    long_name = "A" * 101
    category = CategoryFactory.build(name=long_name)
    with pytest.raises(ValidationError):
        category.full_clean()


@pytest.mark.django_db
def test_category_type_is_too_long():
    """Check validation for invalid Category type choice."""
    user = UserFactory()
    category = CategoryFactory.build(type="FANTASY", user=user)
    with pytest.raises(ValidationError):
        category.full_clean()


@pytest.mark.django_db
def test_category_related_with_user():
    """Check that Category is correctly related to user."""
    user = UserFactory()
    category = CategoryFactory(user=user)
    assert Category.objects.count() == 1
    assert Category.objects.first().user == user


@pytest.mark.django_db
def test_delete_category_sets_transaction_category_to_null():
    """
    Check that deleting Category sets transaction category to NULL (SET_NULL).
    """
    user = UserFactory()
    account = AccountFactory(user=user)
    category = CategoryFactory(name="Food", type="EXPENSE")
    transaction = TransactionFactory(
        user=user,
        account=account,
        type="EXPENSE",
        category=category,
        amount=Decimal("25.00"),
    )
    assert Transaction.objects.first().category == category
    category.delete()
    assert Transaction.objects.first().category is None
    assert Category.objects.count() == 0


# ====================================================
# --- TAGS ---
# ====================================================
@pytest.mark.django_db
def test_tag_has_valid_data():
    """Check that Tag stores valid data correctly."""
    user = UserFactory()
    tag = TagFactory(user=user, name="Tag_name")
    assert Tag.objects.count() == 1
    assert Tag.objects.first().name == "Tag_name"


@pytest.mark.django_db
def test_tag_has_invalid_data():
    """Check validation for too long Tag name."""
    long_name = "A" * 51
    tag = TagFactory.build(name=long_name)
    with pytest.raises(ValidationError):
        tag.full_clean()
