from django.db import models
from django.contrib.auth.models import User
import uuid
from django.utils import timezone
from datetime import timedelta

# 1. HISOB (Account) - Naqd pul, Karta, Valyuta
class Account(models.Model):
    ACCOUNT_TYPES = [
        ('cash', 'Naqd pul'),
        ('card', 'Karta'),
        ('currency', 'Valyuta'),
    ]
    
    CURRENCY_CHOICES = [
        ('UZS', 'So\'m'),
        ('USD', 'Dollar'),
        ('EUR', 'Evro'),
        ('RUB', 'Rubl'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='accounts')
    name = models.CharField(max_length=100, verbose_name='Hisob nomi')
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES, verbose_name='Hisob turi')
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='UZS', verbose_name='Valyuta')  # YANGI
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Balans')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Hisob'
        verbose_name_plural = 'Hisoblar'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.get_account_type_display()})"


# 2. KIRIM KATEGORIYASI (Income Category)
class IncomeCategory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='income_categories')
    name = models.CharField(max_length=100, verbose_name='Kategoriya nomi')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Kirim kategoriyasi'
        verbose_name_plural = 'Kirim kategoriyalari'
        ordering = ['name']
    
    def __str__(self):
        return self.name


# 3. CHIQIM KATEGORIYASI (Expense Category)
class ExpenseCategory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='expense_categories')
    name = models.CharField(max_length=100, verbose_name='Kategoriya nomi')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Chiqim kategoriyasi'
        verbose_name_plural = 'Chiqim kategoriyalari'
        ordering = ['name']
    
    def __str__(self):
        return self.name


# 4. KIRIM (Income)
class Income(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='incomes')
    account = models.ForeignKey(Account, on_delete=models.CASCADE, verbose_name='Hisob')
    category = models.ForeignKey(IncomeCategory, on_delete=models.SET_NULL, null=True, verbose_name='Kategoriya')
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Summa')
    date = models.DateField(verbose_name='Sana')
    description = models.TextField(blank=True, null=True, verbose_name='Izoh')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Kirim'
        verbose_name_plural = 'Kirimlar'
        ordering = ['-date', '-created_at']
    
    def __str__(self):
        return f"{self.category} - {self.amount} so'm"


# 5. CHIQIM (Expense)
class Expense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='expenses')
    account = models.ForeignKey(Account, on_delete=models.CASCADE, verbose_name='Hisob')
    category = models.ForeignKey(ExpenseCategory, on_delete=models.SET_NULL, null=True, verbose_name='Kategoriya')
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Summa')
    date = models.DateField(verbose_name='Sana')
    description = models.TextField(blank=True, null=True, verbose_name='Izoh')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Chiqim'
        verbose_name_plural = 'Chiqimlar'
        ordering = ['-date', '-created_at']
    
    def __str__(self):
        return f"{self.category} - {self.amount} so'm"
    



# Email Verification Model
class EmailVerification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='email_verifications')
    code = models.CharField(max_length=6)  # 6 raqamli kod
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_verified = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(minutes=10)  # 10 daqiqa amal qiladi
        super().save(*args, **kwargs)
    
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    class Meta:
        verbose_name = 'Email Verification'
        verbose_name_plural = 'Email Verifications'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.code}"


# Password Reset Token Model
class PasswordResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_reset_tokens')
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(hours=1)  # 1 soat amal qiladi
        super().save(*args, **kwargs)
    
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    class Meta:
        verbose_name = 'Password Reset Token'
        verbose_name_plural = 'Password Reset Tokens'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.token}"
    


# Currency Rate Model (Valyuta kurslari)
class CurrencyRate(models.Model):
    CURRENCY_CHOICES = [
        ('USD', 'Dollar'),
        ('EUR', 'Evro'),
        ('RUB', 'Rubl'),
    ]
    
    code = models.CharField(max_length=3, choices=CURRENCY_CHOICES, unique=True, verbose_name='Valyuta kodi')
    rate_to_uzs = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='1 valyuta = ? so\'m')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Yangilangan')
    
    class Meta:
        verbose_name = 'Valyuta kursi'
        verbose_name_plural = 'Valyuta kurslari'
        ordering = ['code']
    
    def __str__(self):
        return f"1 {self.code} = {self.rate_to_uzs} so'm"
    