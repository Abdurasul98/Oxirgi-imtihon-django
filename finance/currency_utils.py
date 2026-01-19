from decimal import Decimal
from .models import CurrencyRate

def get_exchange_rates():
    rates = {'UZS': Decimal('1.00')}
    
    for currency_rate in CurrencyRate.objects.all():
        rates[currency_rate.code] = currency_rate.rate_to_uzs
    
    # MUHIM: Agar database'da kurslar bo'lmasa, default qiymatlar
    if 'USD' not in rates:
        rates['USD'] = Decimal('12500.00')
    if 'EUR' not in rates:
        rates['EUR'] = Decimal('14200.00')
    if 'RUB' not in rates:
        rates['RUB'] = Decimal('130.00')
    
    return rates


def convert_amount(amount, from_currency, to_currency, rates=None):
    
    if rates is None:
        rates = get_exchange_rates()
    
    amount = Decimal(str(amount))
    
    # Agar bir xil valyuta bo'lsa
    if from_currency == to_currency:
        return amount
    
    # MUHIM: Valyuta mavjudligini tekshirish
    if from_currency not in rates:
        # Agar from_currency UZS bolmasa va rates'da yoq bolsa
        if from_currency != 'UZS':
            rates = get_exchange_rates()  # Qayta olish
        if from_currency not in rates and from_currency != 'UZS':
            return amount  # Konvert qilish mumkin emas original qaytarish
    
    if to_currency not in rates:
        if to_currency != 'UZS':
            rates = get_exchange_rates()
        if to_currency not in rates and to_currency != 'UZS':
            return amount
    
    # Birinchi UZS ga otkazish
    if from_currency == 'UZS':
        amount_in_uzs = amount
    else:
        amount_in_uzs = amount * rates.get(from_currency, Decimal('1.00'))
    
    # Keyin kerakli valyutaga
    if to_currency == 'UZS':
        return amount_in_uzs
    else:
        rate = rates.get(to_currency, Decimal('1.00'))
        if rate > 0:
            return amount_in_uzs / rate
        else:
            return amount_in_uzs

def get_currency_symbol(currency_code):
    symbols = {
        'UZS': 'so\'m',
        'USD': '$',
        'EUR': '€',
        'RUB': '₽',
    }
    return symbols.get(currency_code, currency_code)