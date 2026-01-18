from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Income, Expense, Account, IncomeCategory, ExpenseCategory

# User Registration Form
class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
    
    def __init__(self, *args, **kwargs):
        super(UserRegisterForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Bu email allaqachon ro\'yxatdan o\'tgan!')
        return email

# Income Form
class IncomeForm(forms.ModelForm):
    class Meta:
        model = Income
        fields = ['account', 'category', 'amount', 'date', 'description']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Faqat user'ning o'z hisoblari va kategoriyalarini ko'rsatish
        self.fields['account'].queryset = Account.objects.filter(user=user)
        self.fields['category'].queryset = IncomeCategory.objects.filter(user=user)

# Expense Form (TO'LIQ VERSIYA - edit uchun ham)
class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['account', 'category', 'amount', 'date', 'description']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['account'].queryset = Account.objects.filter(user=user)
        self.fields['category'].queryset = ExpenseCategory.objects.filter(user=user)
        self.user = user
    
    def clean(self):
        cleaned_data = super().clean()
        account = cleaned_data.get('account')
        amount = cleaned_data.get('amount')
        
        if account and amount:
            # Agar edit qilinyotgan bo'lsa (instance mavjud)
            if self.instance and self.instance.pk:
                # Eski summa qaytariladi, yangi summa olinadi
                old_amount = self.instance.amount
                old_account = self.instance.account
                
                # Agar hisob o'zgarmagan bo'lsa
                if old_account == account:
                    # Farqni hisoblaymiz
                    difference = amount - old_amount
                    available_balance = account.balance
                    
                    if difference > available_balance:
                        raise forms.ValidationError(
                            f"Balansda yetarli mablag' yo'q! "
                            f"Hisob: {account.name} - Mavjud: {available_balance} {account.currency}, "
                            f"Qo'shimcha kerak: {difference} {account.currency}"
                        )
                else:
                    # Agar hisob o'zgargan bo'lsa
                    if account.balance < amount:
                        raise forms.ValidationError(
                            f"Yangi hisobda yetarli mablag' yo'q! "
                            f"Hisob: {account.name} - Mavjud: {account.balance} {account.currency}, "
                            f"Kerak: {amount} {account.currency}"
                        )
            else:
                # Yangi chiqim qo'shilmoqda
                if account.balance < amount:
                    raise forms.ValidationError(
                        f"Balansda yetarli mablag' yo'q! "
                        f"Hisob: {account.name} - Mavjud: {account.balance} {account.currency}, "
                        f"Kerak: {amount} {account.currency}"
                    )
        
        return cleaned_data

# Account Form
class AccountForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ['name', 'account_type', 'currency', 'balance']
        widgets = {
            'currency': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Agar "Valyuta" tipini tanlasa, currency field ko'rinadi
        # JavaScript orqali buni qilish mumkin, lekin hozircha hammasi ko'rinadi

# Income Category Form
class IncomeCategoryForm(forms.ModelForm):
    class Meta:
        model = IncomeCategory
        fields = ['name']

# Expense Category Form
class ExpenseCategoryForm(forms.ModelForm):
    class Meta:
        model = ExpenseCategory
        fields = ['name']