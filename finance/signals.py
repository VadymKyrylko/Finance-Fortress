from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from finance.models import Transaction


def apply_transaction_effect(transaction):
    """Applies the transaction's impact to balances (as when created)."""
    transaction.account.refresh_from_db()

    if transaction.type == "INCOME":
        transaction.account.balance += transaction.amount
    elif transaction.type == "EXPENSE":
        transaction.account.balance -= transaction.amount
    elif transaction.type == "TRANSFER":
        transaction.account.balance -= transaction.amount
        if transaction.target_account:
            transaction.target_account.refresh_from_db()
            transaction.target_account.balance += transaction.amount
            transaction.target_account.save()
    transaction.account.save()


def revert_transaction_effect(transaction):
    """Undoes the transaction's effect on balances (as in deletion)."""
    transaction.account.refresh_from_db()
    if transaction.type == "INCOME":
        transaction.account.balance -= transaction.amount
    elif transaction.type == "EXPENSE":
        transaction.account.balance += transaction.amount
    elif transaction.type == "TRANSFER":
        transaction.account.balance += transaction.amount
        if transaction.target_account:
            transaction.target_account.refresh_from_db()
            transaction.target_account.balance -= transaction.amount
            transaction.target_account.save()

    transaction.account.save()


@receiver(pre_save, sender=Transaction)
def handle_transaction_update(sender, instance, **kwargs):
    """
    Called BEFORE saving.
    If the transaction already exists (this is an edit), we need to
    find the old version of it in the database and undo its effects.
    """
    if instance.pk:
        try:
            old_instance = sender.objects.get(pk=instance.pk)
            revert_transaction_effect(old_instance)
        except sender.DoesNotExist:
            pass


@receiver(post_save, sender=Transaction)
def update_balance_on_save(sender, instance, created, **kwargs):
    """
    Called AFTER saving.
    Apply new data to balance.
    """
    apply_transaction_effect(instance)


@receiver(post_delete, sender=Transaction)
def update_balance_on_delete(sender, instance, **kwargs):
    """
    Called AFTER deletion.
    Undo the effect of the transaction.
    """
    revert_transaction_effect(instance)
