from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from parts_inventory.models import Supplier, Sale, Purchase

# استيراد نماذج الضرائب
from .tax_models import TaxRate, TaxCategory, SaleTax, PurchaseTax, TaxReport


class FinancialAccount(models.Model):
    """نموذج للحسابات المالية"""
    ACCOUNT_TYPES = [
        ('asset', _('أصول')),
        ('liability', _('التزامات')),
        ('equity', _('حقوق ملكية')),
        ('revenue', _('إيرادات')),
        ('expense', _('مصروفات')),
    ]
    
    name = models.CharField(_('اسم الحساب'), max_length=100)
    account_type = models.CharField(_('نوع الحساب'), max_length=20, choices=ACCOUNT_TYPES)
    code = models.CharField(_('رمز الحساب'), max_length=20, unique=True)
    parent = models.ForeignKey('self', verbose_name=_('الحساب الأب'), on_delete=models.CASCADE, 
                               blank=True, null=True, related_name='children')
    description = models.TextField(_('الوصف'), blank=True, null=True)
    is_active = models.BooleanField(_('نشط'), default=True)
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاريخ التحديث'), auto_now=True)
    
    class Meta:
        verbose_name = _('حساب مالي')
        verbose_name_plural = _('الحسابات المالية')
        ordering = ['code', 'name']
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    @property
    def balance(self):
        """حساب الرصيد الحالي للحساب"""
        # حساب مجموع المدين
        debit_sum = self.transactions_as_debit.aggregate(models.Sum('amount'))['amount__sum'] or 0
        # حساب مجموع الدائن
        credit_sum = self.transactions_as_credit.aggregate(models.Sum('amount'))['amount__sum'] or 0
        
        # حساب الرصيد حسب نوع الحساب
        if self.account_type in ['asset', 'expense']:
            return debit_sum - credit_sum
        else:  # liability, equity, revenue
            return credit_sum - debit_sum


class Transaction(models.Model):
    """نموذج للمعاملات المالية"""
    TRANSACTION_TYPES = [
        ('sale', _('بيع')),
        ('purchase', _('شراء')),
        ('expense', _('مصروف')),
        ('income', _('إيراد')),
        ('transfer', _('تحويل')),
        ('adjustment', _('تسوية')),
    ]
    
    transaction_date = models.DateField(_('تاريخ المعاملة'))
    transaction_type = models.CharField(_('نوع المعاملة'), max_length=20, choices=TRANSACTION_TYPES)
    reference_number = models.CharField(_('رقم المرجع'), max_length=50, blank=True, null=True)
    description = models.TextField(_('الوصف'), blank=True, null=True)
    debit_account = models.ForeignKey(FinancialAccount, verbose_name=_('الحساب المدين'), 
                                     on_delete=models.CASCADE, related_name='transactions_as_debit')
    credit_account = models.ForeignKey(FinancialAccount, verbose_name=_('الحساب الدائن'), 
                                      on_delete=models.CASCADE, related_name='transactions_as_credit')
    amount = models.DecimalField(_('المبلغ'), max_digits=10, decimal_places=2)
    sale = models.ForeignKey(Sale, verbose_name=_('عملية البيع'), on_delete=models.SET_NULL, 
                            blank=True, null=True, related_name='transactions')
    purchase = models.ForeignKey(Purchase, verbose_name=_('عملية الشراء'), on_delete=models.SET_NULL, 
                                blank=True, null=True, related_name='transactions')
    created_by = models.ForeignKey(User, verbose_name=_('تم الإنشاء بواسطة'), 
                                  on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاريخ التحديث'), auto_now=True)
    
    class Meta:
        verbose_name = _('معاملة مالية')
        verbose_name_plural = _('المعاملات المالية')
        ordering = ['-transaction_date', '-created_at']
    
    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.amount} - {self.transaction_date}"


class Debt(models.Model):
    """نموذج للديون والمديونيات"""
    DEBT_TYPES = [
        ('receivable', _('مستحق لنا')),  # مديونية على الآخرين
        ('payable', _('مستحق علينا')),    # مديونية علينا للآخرين
    ]
    
    debt_type = models.CharField(_('نوع الدين'), max_length=20, choices=DEBT_TYPES)
    supplier = models.ForeignKey(Supplier, verbose_name=_('المورد'), on_delete=models.CASCADE, 
                                blank=True, null=True, related_name='debts')
    customer_name = models.CharField(_('اسم العميل'), max_length=100, blank=True, null=True)
    amount = models.DecimalField(_('المبلغ الأصلي'), max_digits=10, decimal_places=2)
    remaining_amount = models.DecimalField(_('المبلغ المتبقي'), max_digits=10, decimal_places=2)
    due_date = models.DateField(_('تاريخ الاستحقاق'))
    description = models.TextField(_('الوصف'), blank=True, null=True)
    sale = models.ForeignKey(Sale, verbose_name=_('عملية البيع'), on_delete=models.SET_NULL, 
                            blank=True, null=True, related_name='debts')
    purchase = models.ForeignKey(Purchase, verbose_name=_('عملية الشراء'), on_delete=models.SET_NULL, 
                                blank=True, null=True, related_name='debts')
    is_paid = models.BooleanField(_('تم السداد'), default=False)
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاريخ التحديث'), auto_now=True)
    
    class Meta:
        verbose_name = _('دين')
        verbose_name_plural = _('الديون')
        ordering = ['due_date', '-created_at']
    
    def __str__(self):
        if self.debt_type == 'receivable':
            entity = self.customer_name or 'عميل'
        else:
            entity = self.supplier.name if self.supplier else 'مورد'
        return f"{self.get_debt_type_display()} - {entity} - {self.remaining_amount}"


class DebtPayment(models.Model):
    """نموذج لدفعات سداد الديون"""
    debt = models.ForeignKey(Debt, verbose_name=_('الدين'), on_delete=models.CASCADE, related_name='payments')
    payment_date = models.DateField(_('تاريخ الدفع'))
    amount = models.DecimalField(_('المبلغ المدفوع'), max_digits=10, decimal_places=2)
    payment_method = models.CharField(_('طريقة الدفع'), max_length=50)
    reference_number = models.CharField(_('رقم المرجع'), max_length=50, blank=True, null=True)
    notes = models.TextField(_('ملاحظات'), blank=True, null=True)
    created_by = models.ForeignKey(User, verbose_name=_('تم الإنشاء بواسطة'), 
                                  on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('دفعة سداد')
        verbose_name_plural = _('دفعات السداد')
        ordering = ['-payment_date']
    
    def __str__(self):
        return f"دفعة {self.amount} بتاريخ {self.payment_date}"
    
    def save(self, *args, **kwargs):
        # تحديث المبلغ المتبقي في الدين
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new:  # إذا كانت دفعة جديدة
            self.debt.remaining_amount -= self.amount
            if self.debt.remaining_amount <= 0:
                self.debt.is_paid = True
            self.debt.save()


class ProfitLossReport(models.Model):
    """نموذج لتقارير الربح والخسارة"""
    start_date = models.DateField(_('تاريخ البداية'))
    end_date = models.DateField(_('تاريخ النهاية'))
    total_sales = models.DecimalField(_('إجمالي المبيعات'), max_digits=12, decimal_places=2)
    total_cost_of_goods = models.DecimalField(_('إجمالي تكلفة البضائع المباعة'), max_digits=12, decimal_places=2)
    gross_profit = models.DecimalField(_('إجمالي الربح'), max_digits=12, decimal_places=2)
    total_expenses = models.DecimalField(_('إجمالي المصروفات'), max_digits=12, decimal_places=2)
    net_profit = models.DecimalField(_('صافي الربح'), max_digits=12, decimal_places=2)
    notes = models.TextField(_('ملاحظات'), blank=True, null=True)
    created_by = models.ForeignKey(User, verbose_name=_('تم الإنشاء بواسطة'), 
                                  on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('تقرير الربح والخسارة')
        verbose_name_plural = _('تقارير الربح والخسارة')
        ordering = ['-end_date']
    
    def __str__(self):
        return f"تقرير الربح والخسارة ({self.start_date} - {self.end_date})"