from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Income, Expense

# Kirim qo'shilganda balansni oshirish
@receiver(post_save, sender=Income)
def update_balance_on_income(sender, instance, created, **kwargs):
    if created:  # Faqat yangi kirim qo'shilganda
        account = instance.account
        account.balance += instance.amount
        account.save()

# Kirim o'chirilganda balansni kamaytirish
@receiver(post_delete, sender=Income)
def revert_balance_on_income_delete(sender, instance, **kwargs):
    account = instance.account
    account.balance -= instance.amount
    account.save()

# Chiqim qo'shilganda balansni kamaytirish
@receiver(post_save, sender=Expense)
def update_balance_on_expense(sender, instance, created, **kwargs):
    if created:  # Faqat yangi chiqim qo'shilganda
        account = instance.account
        account.balance -= instance.amount
        account.save()

# Chiqim o'chirilganda balansni oshirish
@receiver(post_delete, sender=Expense)
def revert_balance_on_expense_delete(sender, instance, **kwargs):
    account = instance.account
    account.balance += instance.amount
    account.save()