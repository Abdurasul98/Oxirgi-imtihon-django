import random
from django.core.mail import send_mail
from django.conf import settings

def generate_verification_code():
    """6 raqamli tasodifiy kod yaratish"""
    return str(random.randint(100000, 999999))

def send_verification_email(user, code):
    """Email verification kodi yuborish"""
    subject = 'Email tasdiqlanh kodi'
    message = f"""
    Salom {user.username}!
    
    Ro'yxatdan o'tishni yakunlash uchun quyidagi kodni kiriting:
    
    KOD: {code}
    
    Bu kod 10 daqiqa davomida amal qiladi.
    
    Agar siz ro'yxatdan o'tmagan bo'lsangiz, bu xabarni e'tiborga olmang.
    
    Hurmat bilan,
    Finance Team
    """
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@finance.uz',
        [user.email],
        fail_silently=False,
    )

def send_password_reset_email(user, token):
    """Parolni tiklash linki yuborish"""
    reset_url = f"http://127.0.0.1:8000/reset-password/{token}/"
    
    subject = 'Parolni tiklash'
    message = f"""
    Salom {user.username}!
    
    Parolni tiklash uchun quyidagi linkka o'ting:
    
    {reset_url}
    
    Bu link 1 soat davomida amal qiladi.
    
    Agar siz parolni tiklahmagan bo'lsangiz, bu xabarni e'tiborga olmang.
    
    Hurmat bilan,
    Finance Team
    """
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@finance.uz',
        [user.email],
        fail_silently=False,
    )