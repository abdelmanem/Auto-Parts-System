from django.urls import path
from . import views
from . import tax_views

app_name = 'financial'

urlpatterns = [
    # حركات المخزون
    path('inventory-movements/', views.inventory_movements_list, name='inventory_movements_list'),
    path('inventory-movements/add/', views.add_inventory_movement, name='add_inventory_movement'),
    path('', views.financial_dashboard, name='dashboard'),
    path('accounts/', views.accounts_list, name='accounts_list'),
    path('transactions/', views.transactions_list, name='transactions_list'),
    path('debts/', views.debts_list, name='debts_list'),
    path('debts/add/', views.add_debt, name='add_debt'),
    path('profit-loss/', views.profit_loss_report, name='profit_loss_report'),
    
    # مسارات نظام الضرائب
    path('taxes/', tax_views.tax_dashboard, name='tax_dashboard'),
    path('taxes/rates/', tax_views.tax_rates_list, name='tax_rates_list'),
    path('taxes/rates/add/', tax_views.add_tax_rate, name='add_tax_rate'),
    path('taxes/rates/<int:tax_rate_id>/edit/', tax_views.edit_tax_rate, name='edit_tax_rate'),
    path('taxes/rates/<int:tax_rate_id>/delete/', tax_views.delete_tax_rate, name='delete_tax_rate'),
    path('taxes/sales/', tax_views.sales_taxes_list, name='sales_taxes_list'),
    path('taxes/sales/add/', tax_views.add_sales_tax, name='add_sales_tax'),
    path('taxes/purchases/', tax_views.purchase_taxes_list, name='purchase_taxes_list'),
    path('taxes/purchases/add/', tax_views.add_purchase_tax, name='add_purchase_tax'),
    path('taxes/reports/', tax_views.tax_reports_list, name='tax_reports_list'),
    path('taxes/reports/generate/', tax_views.generate_tax_report, name='generate_tax_report'),
    path('taxes/reports/<int:report_id>/', tax_views.tax_report_detail, name='tax_report_detail'),
    path('taxes/reports/<int:report_id>/update-status/', tax_views.update_tax_report_status, name='update_tax_report_status'),
]