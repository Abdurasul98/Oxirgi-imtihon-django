from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from .models import Income, Expense


@receiver(post_save, sender=Income)
def update_balance_on_income(sender, instance, created, **kwargs):
    if created:
        account = instance.account
        account.balance += instance.amount
        account.save()


@receiver(post_delete, sender=Income)
def revert_balance_on_income_delete(sender, instance, **kwargs):
    account = instance.account
    account.balance -= instance.amount
    account.save()


@receiver(pre_save, sender=Expense)
def check_balance_before_expense(sender, instance, **kwargs):
    if not instance.pk:
        account = instance.account
        if account.balance < instance.amount:
            raise ValidationError(
                f"Balansda yetarli mablag' yo'q! "
                f"Mavjud: {account.balance}, Kerak: {instance.amount}"
            )


@receiver(post_save, sender=Expense)
def update_balance_on_expense(sender, instance, created, **kwargs):
    if created:
        account = instance.account
        account.balance -= instance.amount
        account.save()

@receiver(post_delete, sender=Expense)
def revert_balance_on_expense_delete(sender, instance, **kwargs):
    account = instance.account
    account.balance += instance.amount
    account.save()