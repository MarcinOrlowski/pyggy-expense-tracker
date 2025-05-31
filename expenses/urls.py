from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Expense Management
    path('expenses/', views.expense_list, name='expense_list'),
    path('expenses/create/', views.expense_create, name='expense_create'),
    path('expenses/<int:pk>/', views.expense_detail, name='expense_detail'),
    path('expenses/<int:pk>/edit/', views.expense_edit, name='expense_edit'),
    path('expenses/<int:pk>/delete/', views.expense_delete, name='expense_delete'),
    
    # Month Processing
    path('months/', views.month_list, name='month_list'),
    path('months/<int:year>/<int:month>/', views.month_detail, name='month_detail'),
    path('months/<int:year>/<int:month>/delete/', views.month_delete, name='month_delete'),
    path('months/process/', views.month_process, name='month_process'),
    
    # Payment Processing
    path('expense-items/<int:pk>/pay/', views.expense_item_pay, name='expense_item_pay'),
    path('expense-items/<int:pk>/unpay/', views.expense_item_unpay, name='expense_item_unpay'),
    
    # Reference Data
    path('payees/', views.payee_list, name='payee_list'),
    path('payees/create/', views.payee_create, name='payee_create'),
    path('payees/<int:pk>/edit/', views.payee_edit, name='payee_edit'),
    path('payees/<int:pk>/delete/', views.payee_delete, name='payee_delete'),
    path('payees/<int:pk>/hide/', views.payee_hide, name='payee_hide'),
    path('payees/<int:pk>/unhide/', views.payee_unhide, name='payee_unhide'),
    path('payment-methods/', views.payment_method_list, name='payment_method_list'),
]