from decimal import Decimal
from .models import CurrencyRate

def get_exchange_rates():
    """
    Barcha valyuta kurslarini olish
    Returns: {'USD': 12500, 'EUR': 14200, 'RUB': 130}
    """
    rates = {'UZS': Decimal('1.00')}  # 1 so'm = 1 so'm
    
    for currency_rate in CurrencyRate.objects.all():
        rates[currency_rate.code] = currency_rate.rate_to_uzs
    
    return rates


def convert_amount(amount, from_currency, to_currency, rates=None):
    """
    Summani bir valyutadan ikkinchisiga konvertatsiya qilish
    
    Args:
        amount: Summa (masalan: 5000000 yoki 500)
        from_currency: Qaysi valyutadan (masalan: 'UZS' yoki 'USD')
        to_currency: Qaysi valyutaga (masalan: 'USD' yoki 'EUR')
        rates: Kurslar dictionary (agar berilmasa, database'dan olinadi)
    
    Returns:
        Konvert qilingan summa
    
    Example:
        >>> convert_amount(12500, 'UZS', 'USD')
        1.00
        >>> convert_amount(1, 'USD', 'UZS')
        12500.00
    """
    
    if rates is None:
        rates = get_exchange_rates()
    
    amount = Decimal(str(amount))
    
    # Agar bir xil valyuta bo'lsa
    if from_currency == to_currency:
        return amount
    
    # Birinchi UZS ga o'tkazish
    if from_currency == 'UZS':
        amount_in_uzs = amount
    else:
        amount_in_uzs = amount * rates[from_currency]
    
    # Keyin kerakli valyutaga
    if to_currency == 'UZS':
        return amount_in_uzs
    else:
        return amount_in_uzs / rates[to_currency]


def get_currency_symbol(currency_code):
    """
    Valyuta belgisini olish
    """
    symbols = {
        'UZS': 'so\'m',
        'USD': '$',
        'EUR': '€',
        'RUB': '₽',
    }
    return symbols.get(currency_code, currency_code)