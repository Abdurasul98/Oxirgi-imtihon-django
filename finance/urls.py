from django.urls import path
from .views import register_view,login_view,logout_view,dashboard_view,income_list_view,income_add_view,income_edit_view,income_delete_view,expense_list_view,expense_add_view,expense_edit_view,expense_delete_view,account_list_view,account_add_view,category_list_view,reports_view,verify_email_view,resend_verification_code,forgot_password_view,reset_password_view,account_edit_view,account_delete_view

app_name = 'finance'

urlpatterns = [
    # Authentication
    path('register/', register_view, name='register'),
    path('verify-email/<int:user_id>/', verify_email_view, name='verify_email'), 
    path('resend-code/<int:user_id>/', resend_verification_code, name='resend_code'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('forgot-password/', forgot_password_view, name='forgot_password'), 
    path('reset-password/<uuid:token>/', reset_password_view, name='reset_password'),
    
    # Dashboard
    path('', dashboard_view, name='dashboard'),
    
    # Income URLs
    path('income/', income_list_view, name='income_list'),
    path('income/add/', income_add_view, name='income_add'),
    path('income/<int:pk>/edit/', income_edit_view, name='income_edit'),
    path('income/<int:pk>/delete/', income_delete_view, name='income_delete'),
    
    # Expense URLs
    path('expense/', expense_list_view, name='expense_list'),
    path('expense/add/', expense_add_view, name='expense_add'),
    path('expense/<int:pk>/edit/', expense_edit_view, name='expense_edit'),
    path('expense/<int:pk>/delete/', expense_delete_view, name='expense_delete'),
    
    # Account URLs
    path('accounts/', account_list_view, name='account_list'),
    path('accounts/add/', account_add_view, name='account_add'),
    path('accounts/<int:pk>/edit/', account_edit_view, name='account_edit'),  # YANGI
    path('accounts/<int:pk>/delete/', account_delete_view, name='account_delete'),  # YANGI
    
    # Category URLs
    path('categories/', category_list_view, name='category_list'),

    # Reports URL - SHU QATORNI QO'SHING
    path('reports/', reports_view, name='reports'),
]