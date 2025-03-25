from django.contrib import admin
from .models import (
    FinancialAccount, Transaction, Debt,
    DebtPayment, ProfitLossReport
)
from .tax_models import (
    TaxRate, TaxCategory, SaleTax, PurchaseTax, TaxReport
)


@admin.register(FinancialAccount)
class FinancialAccountAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'account_type', 'is_active')
    list_filter = ('account_type', 'is_active')
    search_fields = ('name', 'code')


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_date', 'transaction_type', 'debit_account', 'credit_account', 'amount')
    list_filter = ('transaction_type', 'transaction_date')
    search_fields = ('description', 'reference_number')
    date_hierarchy = 'transaction_date'


class DebtPaymentInline(admin.TabularInline):
    model = DebtPayment
    extra = 1


@admin.register(Debt)
class DebtAdmin(admin.ModelAdmin):
    list_display = ('debt_type', 'get_entity_name', 'amount', 'remaining_amount', 'due_date', 'is_paid')
    list_filter = ('debt_type', 'is_paid', 'due_date')
    search_fields = ('customer_name', 'supplier__name', 'description')
    inlines = [DebtPaymentInline]
    date_hierarchy = 'due_date'
    
    def get_entity_name(self, obj):
        if obj.debt_type == 'receivable':
            return obj.customer_name or 'عميل'
        else:
            return obj.supplier.name if obj.supplier else 'مورد'
    get_entity_name.short_description = 'الجهة'


@admin.register(DebtPayment)
class DebtPaymentAdmin(admin.ModelAdmin):
    list_display = ('debt', 'payment_date', 'amount', 'payment_method')
    list_filter = ('payment_date', 'payment_method')
    search_fields = ('debt__customer_name', 'debt__supplier__name', 'notes')
    date_hierarchy = 'payment_date'


@admin.register(ProfitLossReport)
class ProfitLossReportAdmin(admin.ModelAdmin):
    list_display = ('start_date', 'end_date', 'total_sales', 'total_cost_of_goods', 'gross_profit', 'net_profit')
    list_filter = ('start_date', 'end_date')
    date_hierarchy = 'end_date'
    readonly_fields = ('total_sales', 'total_cost_of_goods', 'gross_profit', 'total_expenses', 'net_profit')


@admin.register(TaxRate)
class TaxRateAdmin(admin.ModelAdmin):
    list_display = ('name', 'rate', 'is_default', 'is_active')
    list_filter = ('is_default', 'is_active')
    search_fields = ('name', 'description')


@admin.register(TaxCategory)
class TaxCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    filter_horizontal = ('tax_rates',)


@admin.register(SaleTax)
class SaleTaxAdmin(admin.ModelAdmin):
    list_display = ('sale', 'tax_rate', 'tax_amount', 'is_paid', 'payment_date')
    list_filter = ('is_paid', 'payment_date', 'tax_rate')
    search_fields = ('sale__invoice_number', 'reference_number', 'notes')
    date_hierarchy = 'payment_date'


@admin.register(PurchaseTax)
class PurchaseTaxAdmin(admin.ModelAdmin):
    list_display = ('purchase', 'tax_rate', 'tax_amount', 'is_deductible', 'is_claimed', 'claim_date')
    list_filter = ('is_deductible', 'is_claimed', 'claim_date', 'tax_rate')
    search_fields = ('purchase__reference_number', 'reference_number', 'notes')
    date_hierarchy = 'claim_date'


@admin.register(TaxReport)
class TaxReportAdmin(admin.ModelAdmin):
    list_display = ('report_type', 'start_date', 'end_date', 'status', 'total_sales_tax', 'total_purchase_tax', 'tax_due')
    list_filter = ('report_type', 'status', 'submission_date')
    search_fields = ('reference_number', 'notes')
    date_hierarchy = 'end_date'
    readonly_fields = ('tax_due',)