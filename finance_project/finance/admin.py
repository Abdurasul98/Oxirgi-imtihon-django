from django.contrib import admin
from django.db.models import Sum
from .models import Account, IncomeCategory, ExpenseCategory, Income, Expense,EmailVerification, PasswordResetToken,CurrencyRate

# Account Admin
@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ['name', 'account_type', 'balance', 'user', 'created_at']
    list_filter = ['account_type', 'user', 'created_at']
    search_fields = ['name', 'user__username']
    readonly_fields = ['created_at']
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)

# Income Category Admin
@admin.register(IncomeCategory)
class IncomeCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'total_income', 'created_at']
    search_fields = ['name', 'user__username']
    readonly_fields = ['created_at']
    
    def total_income(self, obj):
        total = Income.objects.filter(category=obj).aggregate(Sum('amount'))['amount__sum'] or 0
        return f"{total:,.0f} so'm"
    total_income.short_description = 'Jami kirim'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)

# Expense Category Admin
@admin.register(ExpenseCategory)
class ExpenseCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'total_expense', 'created_at']
    search_fields = ['name', 'user__username']
    readonly_fields = ['created_at']
    
    def total_expense(self, obj):
        total = Expense.objects.filter(category=obj).aggregate(Sum('amount'))['amount__sum'] or 0
        return f"{total:,.0f} so'm"
    total_expense.short_description = 'Jami chiqim'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)

# Income Admin
@admin.register(Income)
class IncomeAdmin(admin.ModelAdmin):
    list_display = ['date', 'category', 'amount', 'account', 'user', 'created_at']
    list_filter = ['date', 'category', 'account', 'user']
    search_fields = ['description', 'user__username']
    date_hierarchy = 'date'
    readonly_fields = ['created_at']
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)

# Expense Admin
@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ['date', 'category', 'amount', 'account', 'user', 'created_at']
    list_filter = ['date', 'category', 'account', 'user']
    search_fields = ['description', 'user__username']
    date_hierarchy = 'date'
    readonly_fields = ['created_at']
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)
    


@admin.register(EmailVerification)
class EmailVerificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'code', 'is_verified', 'created_at', 'expires_at']
    list_filter = ['is_verified', 'created_at']
    search_fields = ['user__username', 'code']

@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    list_display = ['user', 'token', 'is_used', 'created_at', 'expires_at']
    list_filter = ['is_used', 'created_at']
    search_fields = ['user__username']


@admin.register(CurrencyRate)
class CurrencyRateAdmin(admin.ModelAdmin):
    list_display = ['code', 'rate_to_uzs', 'updated_at']
    list_editable = ['rate_to_uzs']
    
    def has_delete_permission(self, request, obj=None):
        # Kurslarni o'chirib bo'lmaydi, faqat tahrirlash mumkin
        return False