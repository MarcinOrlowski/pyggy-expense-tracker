from django.urls import path
from . import views

urlpatterns = [
    # Budget Management (default page)
    path('', views.budget_list, name='budget_list'),
    path('budgets/', views.budget_list, name='budget_list'),
    path('budgets/create/', views.budget_create, name='budget_create'),
    path('budgets/<int:pk>/edit/', views.budget_edit, name='budget_edit'),
    path('budgets/<int:pk>/delete/', views.budget_delete, name='budget_delete'),
    
    # Budget-scoped URLs
    path('budgets/<int:budget_id>/dashboard/', views.dashboard, name='dashboard'),
    
    # Expense Management (budget-scoped)
    path('budgets/<int:budget_id>/expenses/', views.expense_list, name='expense_list'),
    path('budgets/<int:budget_id>/expenses/create/', views.expense_create, name='expense_create'),
    path('budgets/<int:budget_id>/expenses/<int:pk>/', views.expense_detail, name='expense_detail'),
    path('budgets/<int:budget_id>/expenses/<int:pk>/edit/', views.expense_edit, name='expense_edit'),
    path('budgets/<int:budget_id>/expenses/<int:pk>/delete/', views.expense_delete, name='expense_delete'),
    
    # Month Processing (budget-scoped)
    path('budgets/<int:budget_id>/months/', views.month_list, name='month_list'),
    path('budgets/<int:budget_id>/months/<int:year>/<int:month>/', views.month_detail, name='month_detail'),
    path('budgets/<int:budget_id>/months/<int:year>/<int:month>/delete/', views.month_delete, name='month_delete'),
    path('budgets/<int:budget_id>/months/process/', views.month_process, name='month_process'),
    
    # Payment Processing (budget-scoped)
    path('budgets/<int:budget_id>/expense-items/<int:pk>/pay/', views.expense_item_pay, name='expense_item_pay'),
    path('budgets/<int:budget_id>/expense-items/<int:pk>/unpay/', views.expense_item_unpay, name='expense_item_unpay'),
    path('budgets/<int:budget_id>/expense-items/<int:pk>/edit/', views.expense_item_edit, name='expense_item_edit'),
    
    # Reference Data (no budget context needed)
    path('payees/', views.payee_list, name='payee_list'),
    path('payees/create/', views.payee_create, name='payee_create'),
    path('payees/<int:pk>/edit/', views.payee_edit, name='payee_edit'),
    path('payees/<int:pk>/delete/', views.payee_delete, name='payee_delete'),
    path('payees/<int:pk>/hide/', views.payee_hide, name='payee_hide'),
    path('payees/<int:pk>/unhide/', views.payee_unhide, name='payee_unhide'),
    path('payment-methods/', views.payment_method_list, name='payment_method_list'),
]