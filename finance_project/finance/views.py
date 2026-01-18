from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from datetime import date, timedelta
from .models import Income, Expense, Account, IncomeCategory, ExpenseCategory,EmailVerification, PasswordResetToken
from .forms import (
    UserRegisterForm, IncomeForm, ExpenseForm, AccountForm,
    IncomeCategoryForm, ExpenseCategoryForm
)
from .utils import generate_verification_code, send_verification_email, send_password_reset_email
from django.contrib.auth.models import User
import uuid
from decimal import Decimal
from .currency_utils import get_exchange_rates, convert_amount, get_currency_symbol
from django.core.exceptions import ValidationError


# ========== AUTHENTICATION VIEWS (YANGILANGAN) ==========

def register_view(request):
    print("="*50)
    print("REGISTER VIEW")
    print(f"User authenticated BEFORE: {request.user.is_authenticated}")
    
    if request.user.is_authenticated:
        print("User allaqachon login qilgan!")
        return redirect('finance:dashboard')
    
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            print(f"User yaratildi: {user.username}, is_active={user.is_active}")
            
            email = form.cleaned_data.get('email')
            
            code = generate_verification_code()
            EmailVerification.objects.create(user=user, code=code)
            print(f"Verification kod: {code}")
            
            try:
                send_verification_email(user, code)
                messages.success(request, f'{email} ga kod yuborildi!')
            except Exception as e:
                messages.error(request, f'Xatolik: {str(e)}')
                user.delete()
                return redirect('finance:register')
            
            print(f"User authenticated AFTER: {request.user.is_authenticated}")
            print(f"Redirecting to verify_email, user_id={user.id}")
            
            return redirect('finance:verify_email', user_id=user.id)
    else:
        form = UserRegisterForm()
    
    return render(request, 'finance/register.html', {'form': form})

def verify_email_view(request, user_id):
    """Email verification kodni tekshirish"""
    try:
        user = User.objects.get(id=user_id, is_active=False)
    except User.DoesNotExist:
        messages.error(request, 'Foydalanuvchi topilmadi yoki allaqachon tasdiqlangan!')
        return redirect('finance:login')
    
    if request.method == 'POST':
        code = request.POST.get('code', '').strip()
        
        try:
            verification = EmailVerification.objects.get(
                user=user, 
                code=code, 
                is_verified=False
            )
            
            if verification.is_expired():
                messages.error(request, 'Kod muddati tugagan! Yangi kod so\'rang.')
            else:
                # Email tasdiqlandi
                verification.is_verified = True
                verification.save()
                
                # Userni activate qilish
                user.is_active = True
                user.save()
                
                # Avtomatik login qilish
                login(request, user)
                
                messages.success(request, 'Email muvaffaqiyatli tasdiqlandi! Xush kelibsiz!')
                return redirect('finance:dashboard')
        
        except EmailVerification.DoesNotExist:
            messages.error(request, 'Noto\'g\'ri kod! Qaytadan urinib ko\'ring.')
    
    return render(request, 'finance/verify_email.html', {'user': user})


def resend_verification_code(request, user_id):
    """Yangi verification kod yuborish"""
    try:
        user = User.objects.get(id=user_id, is_active=False)
        
        # Eski kodlarni o'chirish
        EmailVerification.objects.filter(user=user, is_verified=False).delete()
        
        # Yangi kod yaratish
        code = generate_verification_code()
        EmailVerification.objects.create(user=user, code=code)
        
        # Email yuborish
        send_verification_email(user, code)
        messages.success(request, 'Yangi tasdiqlash kodi yuborildi!')
        
    except User.DoesNotExist:
        messages.error(request, 'Foydalanuvchi topilmadi!')
    
    return redirect('finance:verify_email', user_id=user_id)


def forgot_password_view(request):
    """Parolni unutdim sahifasi"""
    if request.method == 'POST':
        email = request.POST.get('email')
        
        try:
            user = User.objects.get(email=email)
            
            # Token yaratish
            token = PasswordResetToken.objects.create(user=user)
            
            # Email yuborish
            send_password_reset_email(user, token.token)
            messages.success(request, f'Parolni tiklash linki {email} ga yuborildi!')
            return redirect('finance:login')
            
        except User.DoesNotExist:
            messages.error(request, 'Bu email bilan foydalanuvchi topilmadi!')
    
    return render(request, 'finance/forgot_password.html')


def reset_password_view(request, token):
    """Parolni yangilash sahifasi"""
    try:
        reset_token = PasswordResetToken.objects.get(token=token, is_used=False)
        
        if reset_token.is_expired():
            messages.error(request, 'Bu linkning muddati tugagan!')
            return redirect('finance:forgot_password')
        
        if request.method == 'POST':
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')
            
            if password1 == password2:
                user = reset_token.user
                user.set_password(password1)
                user.save()
                
                # Tokenni ishlatilgan deb belgilash
                reset_token.is_used = True
                reset_token.save()
                
                messages.success(request, 'Parol muvaffaqiyatli o\'zgartirildi! Kirish qiling.')
                return redirect('finance:login')
            else:
                messages.error(request, 'Parollar mos kelmadi!')
        
        return render(request, 'finance/reset_password.html', {'token': token})
        
    except PasswordResetToken.DoesNotExist:
        messages.error(request, 'Noto\'g\'ri yoki ishlatilgan link!')
        return redirect('finance:forgot_password')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Emailni tasdiqlaganini tekshirish
            if user.is_active:
                login(request, user)
                messages.success(request, f'Xush kelibsiz, {username}!')
                return redirect('finance:dashboard')
            else:
                # Email hali tasdiqlanmagan
                messages.warning(request, 'Avval emailingizni tasdiqlang!')
                return redirect('finance:verify_email', user_id=user.id)
        else:
            messages.error(request, 'Login yoki parol noto\'g\'ri!')
    return render(request, 'finance/login.html')


def logout_view(request):
    logout(request)
    messages.success(request, 'Siz tizimdan chiqdingiz!')
    return redirect('finance:login')


# ========== DASHBOARD ==========

@login_required
def dashboard_view(request):
    user = request.user
    
    # Tanlangan valyuta (default: UZS)
    selected_currency = request.GET.get('currency', 'UZS')
    
    # Valyuta kurslarini olish
    rates = get_exchange_rates()
    
    # Barcha hisoblardagi balans
    accounts = Account.objects.filter(user=user)
    
    # Har bir hisob uchun konvert qilingan qiymatni hisoblash
    total_balance_in_selected = Decimal('0.00')
    
    for account in accounts:
        # Original qiymatlarni saqlash
        account.original_balance = account.balance
        account.original_currency = account.currency
        account.original_symbol = get_currency_symbol(account.currency)
        
        # Konvert qilingan qiymat
        account.converted_balance = convert_amount(
            account.balance,
            account.currency,
            selected_currency,
            rates
        )
        
        # Jami balansga qo'shish
        total_balance_in_selected += account.converted_balance
    
    # Bugungi kirim va chiqim (selected valyutada)
    today = date.today()
    today_income_uzs = Income.objects.filter(user=user, date=today).aggregate(total=Sum('amount'))['total'] or 0
    today_expense_uzs = Expense.objects.filter(user=user, date=today).aggregate(total=Sum('amount'))['total'] or 0
    
    today_income = convert_amount(today_income_uzs, 'UZS', selected_currency, rates)
    today_expense = convert_amount(today_expense_uzs, 'UZS', selected_currency, rates)
    
    # Jami kirim va chiqim (selected valyutada)
    total_income_uzs = Income.objects.filter(user=user).aggregate(total=Sum('amount'))['total'] or 0
    total_expense_uzs = Expense.objects.filter(user=user).aggregate(total=Sum('amount'))['total'] or 0
    
    total_income = convert_amount(total_income_uzs, 'UZS', selected_currency, rates)
    total_expense = convert_amount(total_expense_uzs, 'UZS', selected_currency, rates)
    
    # Oxirgi 5 ta tranzaksiya (YANGILANDI)
    recent_incomes = Income.objects.filter(user=user)[:5]
    recent_expenses = Expense.objects.filter(user=user)[:5]
    
    # Har biriga valyuta belgisini qo'shish
    for income in recent_incomes:
        income.currency_symbol = get_currency_symbol(income.account.currency)
    
    for expense in recent_expenses:
        expense.currency_symbol = get_currency_symbol(expense.account.currency)
    
    context = {
        'accounts': accounts,
        'total_balance': total_balance_in_selected,
        'selected_currency': selected_currency,
        'currency_symbol': get_currency_symbol(selected_currency),
        'today_income': today_income,
        'today_expense': today_expense,
        'total_income': total_income,
        'total_expense': total_expense,
        'recent_incomes': recent_incomes,
        'recent_expenses': recent_expenses,
    }
    
    return render(request, 'finance/dashboard.html', context)


# ========== INCOME VIEWS ==========

@login_required
def income_list_view(request):
    incomes = Income.objects.filter(user=request.user)
    total = incomes.aggregate(total=Sum('amount'))['total'] or 0
    
    # Har bir kirim uchun valyuta belgisini qo'shish
    for income in incomes:
        income.currency_symbol = get_currency_symbol(income.account.currency)
    
    context = {
        'incomes': incomes,
        'total': total,
    }
    return render(request, 'finance/income_list.html', context)


@login_required
def income_add_view(request):
    if request.method == 'POST':
        form = IncomeForm(request.user, request.POST)
        if form.is_valid():
            income = form.save(commit=False)
            income.user = request.user
            income.save()
            messages.success(request, 'Kirim muvaffaqiyatli qo\'shildi!')
            return redirect('finance:income_list')
    else:
        form = IncomeForm(request.user)
    return render(request, 'finance/income_form.html', {'form': form, 'title': 'Kirim qo\'shish'})


@login_required
def income_edit_view(request, pk):
    income = get_object_or_404(Income, pk=pk, user=request.user)
    if request.method == 'POST':
        form = IncomeForm(request.user, request.POST, instance=income)
        if form.is_valid():
            form.save()
            messages.success(request, 'Kirim tahrirlandi!')
            return redirect('finance:income_list')
    else:
        form = IncomeForm(request.user, instance=income)
    return render(request, 'finance/income_form.html', {'form': form, 'title': 'Kirimni tahrirlash'})


@login_required
def income_delete_view(request, pk):
    income = get_object_or_404(Income, pk=pk, user=request.user)
    if request.method == 'POST':
        income.delete()
        messages.success(request, 'Kirim o\'chirildi!')
        return redirect('finance:income_list')
    return render(request, 'finance/confirm_delete.html', {'object': income, 'type': 'Kirim'})


# ========== EXPENSE VIEWS ==========

@login_required
def expense_list_view(request):
    expenses = Expense.objects.filter(user=request.user)
    total = expenses.aggregate(total=Sum('amount'))['total'] or 0
    
    # Har bir chiqim uchun valyuta belgisini qo'shish
    for expense in expenses:
        expense.currency_symbol = get_currency_symbol(expense.account.currency)
    
    context = {
        'expenses': expenses,
        'total': total,
    }
    return render(request, 'finance/expense_list.html', context)


@login_required
def expense_add_view(request):
    if request.method == 'POST':
        form = ExpenseForm(request.user, request.POST)
        if form.is_valid():
            try:
                expense = form.save(commit=False)
                expense.user = request.user
                expense.save()
                messages.success(request, 'Chiqim muvaffaqiyatli qo\'shildi!')
                return redirect('finance:expense_list')
            except ValidationError as e:
                messages.error(request, str(e))
        else:
            # Form validation xatoliklari
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
    else:
        form = ExpenseForm(request.user)
    return render(request, 'finance/expense_form.html', {'form': form, 'title': 'Chiqim qo\'shish'})


@login_required
def expense_edit_view(request, pk):
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    if request.method == 'POST':
        form = ExpenseForm(request.user, request.POST, instance=expense)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Chiqim tahrirlandi!')
                return redirect('finance:expense_list')
            except ValidationError as e:
                messages.error(request, str(e))
        else:
            # Form validation xatoliklari
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
    else:
        form = ExpenseForm(request.user, instance=expense)
    return render(request, 'finance/expense_form.html', {'form': form, 'title': 'Chiqimni tahrirlash'})


@login_required
def expense_delete_view(request, pk):
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    if request.method == 'POST':
        expense.delete()
        messages.success(request, 'Chiqim o\'chirildi!')
        return redirect('finance:expense_list')
    return render(request, 'finance/confirm_delete.html', {'object': expense, 'type': 'Chiqim'})



# ========== ACCOUNT VIEWS ==========

@login_required
def account_list_view(request):
    accounts = Account.objects.filter(user=request.user)
    
    # Har bir hisob uchun valyuta belgisini qo'shish
    for account in accounts:
        account.currency_symbol = get_currency_symbol(account.currency)
    
    return render(request, 'finance/account_list.html', {'accounts': accounts})


@login_required
def account_add_view(request):
    if request.method == 'POST':
        form = AccountForm(request.POST)
        if form.is_valid():
            account = form.save(commit=False)
            account.user = request.user
            account.save()
            messages.success(request, 'Hisob qo\'shildi!')
            return redirect('finance:account_list')
    else:
        form = AccountForm()
    return render(request, 'finance/account_form.html', {'form': form})


# ========== CATEGORY VIEWS ==========

@login_required
def category_list_view(request):
    income_categories = IncomeCategory.objects.filter(user=request.user)
    expense_categories = ExpenseCategory.objects.filter(user=request.user)
    
    if request.method == 'POST':
        if 'income_category' in request.POST:
            form = IncomeCategoryForm(request.POST)
            if form.is_valid():
                category = form.save(commit=False)
                category.user = request.user
                category.save()
                messages.success(request, 'Kirim kategoriyasi qo\'shildi!')
        
        elif 'expense_category' in request.POST:
            form = ExpenseCategoryForm(request.POST)
            if form.is_valid():
                category = form.save(commit=False)
                category.user = request.user
                category.save()
                messages.success(request, 'Chiqim kategoriyasi qo\'shildi!')
        
        return redirect('finance:category_list')
    
    context = {
        'income_categories': income_categories,
        'expense_categories': expense_categories,
        'income_form': IncomeCategoryForm(),
        'expense_form': ExpenseCategoryForm(),
    }
    return render(request, 'finance/category_list.html', context)


# ========== HISOBOTLAR (REPORTS) ==========

from datetime import datetime, timedelta
from django.db.models import Q
from django.db.models.functions import TruncDate

@login_required
def reports_view(request):
    user = request.user
    
    # Filter parametrlari
    period = request.GET.get('period', 'month')  # day, week, month, custom
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    # Sana oralig'ini aniqlash
    today = date.today()
    
    if period == 'day':
        date_from = today
        date_to = today
        period_name = 'Bugungi'
    elif period == 'week':
        date_from = today - timedelta(days=today.weekday())  # Hafta boshi (dushanba)
        date_to = today
        period_name = 'Bu hafta'
    elif period == 'month':
        date_from = today.replace(day=1)  # Oy boshi
        date_to = today
        period_name = 'Bu oy'
    elif period == 'custom' and start_date and end_date:
        date_from = datetime.strptime(start_date, '%Y-%m-%d').date()
        date_to = datetime.strptime(end_date, '%Y-%m-%d').date()
        period_name = f'{date_from.strftime("%d.%m.%Y")} - {date_to.strftime("%d.%m.%Y")}'
    else:
        date_from = today.replace(day=1)
        date_to = today
        period_name = 'Bu oy'
    
    # Ma'lumotlarni olish
    incomes = Income.objects.filter(user=user, date__range=[date_from, date_to])
    expenses = Expense.objects.filter(user=user, date__range=[date_from, date_to])
    
    # Jami summa
    total_income = incomes.aggregate(total=Sum('amount'))['total'] or 0
    total_expense = expenses.aggregate(total=Sum('amount'))['total'] or 0
    balance = total_income - total_expense
    
    # Kategoriya bo'yicha statistika (Chiqimlar uchun)
    expense_by_category = expenses.values('category__name').annotate(
        total=Sum('amount')
    ).order_by('-total')
    
    # Kategoriya bo'yicha statistika (Kirimlar uchun)
    income_by_category = incomes.values('category__name').annotate(
        total=Sum('amount')
    ).order_by('-total')
    
    # Hisob bo'yicha statistika
    account_stats = []
    accounts = Account.objects.filter(user=user)
    for account in accounts:
        acc_income = incomes.filter(account=account).aggregate(total=Sum('amount'))['total'] or 0
        acc_expense = expenses.filter(account=account).aggregate(total=Sum('amount'))['total'] or 0
        account_stats.append({
            'account': account,
            'income': acc_income,
            'expense': acc_expense,
        })
    
    # Kunlik statistika (oxirgi 7 kun uchun)
    daily_stats = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        day_income = Income.objects.filter(user=user, date=day).aggregate(total=Sum('amount'))['total'] or 0
        day_expense = Expense.objects.filter(user=user, date=day).aggregate(total=Sum('amount'))['total'] or 0
        daily_stats.append({
            'date': day,
            'income': day_income,
            'expense': day_expense,
        })
    
    context = {
        'period': period,
        'period_name': period_name,
        'date_from': date_from,
        'date_to': date_to,
        'total_income': total_income,
        'total_expense': total_expense,
        'balance': balance,
        'incomes': incomes[:10],  # Oxirgi 10 ta
        'expenses': expenses[:10],  # Oxirgi 10 ta
        'expense_by_category': expense_by_category,
        'income_by_category': income_by_category,
        'account_stats': account_stats,
        'daily_stats': daily_stats,
    }
    
    return render(request, 'finance/reports.html', context)