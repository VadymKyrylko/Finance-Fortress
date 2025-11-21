from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from finance.models import Transaction


@receiver(post_save, sender=Transaction)
def update_balance_on_save(sender, instance, created, **kwargs):
    """
    Called automatically AFTER saving the transaction.
    Works only for NEW transactions (created=True).
    """
    if created:
        account = instance.account
        amount = instance.amount

        if instance.type == "INCOME":
            account.balance += amount
        elif instance.type == "EXPENSE":
            account.balance -= amount
        elif instance.type == "TRANSFER":
            account.balance -= amount
            if instance.target_account:
                instance.target_account.balance += amount
                instance.target_account.save()
        account.save()


@receiver(post_delete, sender=Transaction)
def update_balance_on_delete(sender, instance, **kwargs):
    """
    Called automatically AFTER deleting a transaction.
    We need to 'roll back' the balance changes.
    """
    account = instance.account
    amount = instance.amount
    if instance.type == "INCOME":
        account.balance -= amount
    elif instance.type == "EXPENSE":
        account.balance += amount
    elif instance.type == "TRANSFER":
        account.balance += amount
        if instance.target_account:
            instance.target_account.balance -= amount
            instance.target_account.save()
    account.save()
