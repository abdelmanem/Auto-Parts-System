from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from parts_inventory.models import Sale, Purchase
from decimal import Decimal


class TaxRate(models.Model):
    """نموذج لمعدلات الضرائب"""
    name = models.CharField(_('اسم الضريبة'), max_length=100)
    rate = models.DecimalField(_('معدل الضريبة'), max_digits=5, decimal_places=2, help_text=_('النسبة المئوية للضريبة'))
    is_default = models.BooleanField(_('افتراضي'), default=False)
    description = models.TextField(_('الوصف'), blank=True, null=True)
    is_active = models.BooleanField(_('نشط'), default=True)
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاريخ التحديث'), auto_now=True)
    
    class Meta:
        verbose_name = _('معدل ضريبة')
        verbose_name_plural = _('معدلات الضرائب')
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.rate}%)"
    
    def save(self, *args, **kwargs):
        # التأكد من وجود معدل ضريبة افتراضي واحد فقط
        if self.is_default:
            TaxRate.objects.filter(is_default=True).update(is_default=False)
        super().save(*args, **kwargs)


class TaxCategory(models.Model):
    """نموذج لفئات الضرائب"""
    name = models.CharField(_('اسم الفئة'), max_length=100)
    tax_rates = models.ManyToManyField(TaxRate, verbose_name=_('معدلات الضريبة'), related_name='categories')
    description = models.TextField(_('الوصف'), blank=True, null=True)
    is_active = models.BooleanField(_('نشط'), default=True)
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاريخ التحديث'), auto_now=True)
    
    class Meta:
        verbose_name = _('فئة ضريبية')
        verbose_name_plural = _('فئات الضرائب')
        ordering = ['name']
    
    def __str__(self):
        return self.name


class SaleTax(models.Model):
    """نموذج لضرائب المبيعات"""
    sale = models.ForeignKey(Sale, verbose_name=_('عملية البيع'), on_delete=models.CASCADE, related_name='taxes')
    tax_rate = models.ForeignKey(TaxRate, verbose_name=_('معدل الضريبة'), on_delete=models.PROTECT)
    tax_amount = models.DecimalField(_('مبلغ الضريبة'), max_digits=10, decimal_places=2)
    is_paid = models.BooleanField(_('تم الدفع'), default=False)
    payment_date = models.DateField(_('تاريخ الدفع'), blank=True, null=True)
    reference_number = models.CharField(_('رقم المرجع'), max_length=50, blank=True, null=True)
    notes = models.TextField(_('ملاحظات'), blank=True, null=True)
    created_by = models.ForeignKey(User, verbose_name=_('تم الإنشاء بواسطة'), on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاريخ التحديث'), auto_now=True)
    
    class Meta:
        verbose_name = _('ضريبة مبيعات')
        verbose_name_plural = _('ضرائب المبيعات')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"ضريبة على {self.sale} - {self.tax_amount}"
    
    @classmethod
    def calculate_tax(cls, sale_amount, tax_rate):
        """حساب مبلغ الضريبة بناءً على مبلغ البيع ومعدل الضريبة"""
        return (Decimal(sale_amount) * Decimal(tax_rate.rate)) / Decimal(100)


class PurchaseTax(models.Model):
    """نموذج لضرائب المشتريات"""
    purchase = models.ForeignKey(Purchase, verbose_name=_('عملية الشراء'), on_delete=models.CASCADE, related_name='taxes')
    tax_rate = models.ForeignKey(TaxRate, verbose_name=_('معدل الضريبة'), on_delete=models.PROTECT)
    tax_amount = models.DecimalField(_('مبلغ الضريبة'), max_digits=10, decimal_places=2)
    is_deductible = models.BooleanField(_('قابل للخصم'), default=True, help_text=_('هل يمكن خصم هذه الضريبة من ضرائب المبيعات'))
    is_claimed = models.BooleanField(_('تم المطالبة'), default=False)
    claim_date = models.DateField(_('تاريخ المطالبة'), blank=True, null=True)
    reference_number = models.CharField(_('رقم المرجع'), max_length=50, blank=True, null=True)
    notes = models.TextField(_('ملاحظات'), blank=True, null=True)
    created_by = models.ForeignKey(User, verbose_name=_('تم الإنشاء بواسطة'), on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاريخ التحديث'), auto_now=True)
    
    class Meta:
        verbose_name = _('ضريبة مشتريات')
        verbose_name_plural = _('ضرائب المشتريات')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"ضريبة على {self.purchase} - {self.tax_amount}"
    
    @classmethod
    def calculate_tax(cls, purchase_amount, tax_rate):
        """حساب مبلغ الضريبة بناءً على مبلغ الشراء ومعدل الضريبة"""
        return (Decimal(purchase_amount) * Decimal(tax_rate.rate)) / Decimal(100)


class TaxReport(models.Model):
    """نموذج لتقارير الضرائب"""
    REPORT_TYPES = [
        ('monthly', _('شهري')),
        ('quarterly', _('ربع سنوي')),
        ('annual', _('سنوي')),
        ('custom', _('مخصص')),
    ]
    
    REPORT_STATUS = [
        ('draft', _('مسودة')),
        ('submitted', _('تم التقديم')),
        ('accepted', _('مقبول')),
        ('rejected', _('مرفوض')),
    ]
    
    report_type = models.CharField(_('نوع التقرير'), max_length=20, choices=REPORT_TYPES)
    start_date = models.DateField(_('تاريخ البداية'))
    end_date = models.DateField(_('تاريخ النهاية'))
    status = models.CharField(_('حالة التقرير'), max_length=20, choices=REPORT_STATUS, default='draft')
    total_sales_tax = models.DecimalField(_('إجمالي ضرائب المبيعات'), max_digits=12, decimal_places=2)
    total_purchase_tax = models.DecimalField(_('إجمالي ضرائب المشتريات'), max_digits=12, decimal_places=2)
    tax_due = models.DecimalField(_('الضريبة المستحقة'), max_digits=12, decimal_places=2)
    submission_date = models.DateField(_('تاريخ التقديم'), blank=True, null=True)
    reference_number = models.CharField(_('رقم المرجع'), max_length=50, blank=True, null=True)
    notes = models.TextField(_('ملاحظات'), blank=True, null=True)
    created_by = models.ForeignKey(User, verbose_name=_('تم الإنشاء بواسطة'), on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاريخ التحديث'), auto_now=True)
    
    class Meta:
        verbose_name = _('تقرير ضريبي')
        verbose_name_plural = _('تقارير ضريبية')
        ordering = ['-end_date']
    
    def __str__(self):
        return f"تقرير ضريبي ({self.start_date} - {self.end_date})"
    
    def calculate_tax_due(self):
        """حساب الضريبة المستحقة (الفرق بين ضرائب المبيعات والمشتريات)"""
        return self.total_sales_tax - self.total_purchase_tax