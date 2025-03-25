from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User


class StoreSettings(models.Model):
    store_name = models.CharField(_('اسم المحل'), max_length=200)
    commercial_register = models.CharField(_('السجل التجاري'), max_length=50)
    tax_number = models.CharField(_('البطاقة الضريبية'), max_length=50)
    address = models.TextField(_('العنوان'), blank=True, null=True)
    phone = models.CharField(_('رقم الهاتف'), max_length=20, blank=True, null=True)
    email = models.EmailField(_('البريد الإلكتروني'), blank=True, null=True)
    logo = models.ImageField(_('شعار المحل'), upload_to='store/', blank=True, null=True)
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاريخ التحديث'), auto_now=True)

    class Meta:
        verbose_name = _('إعدادات المحل')
        verbose_name_plural = _('إعدادات المحل')

    def __str__(self):
        return self.store_name

    @classmethod
    def get_settings(cls):
        settings = cls.objects.first()
        if not settings:
            settings = cls.objects.create(
                store_name='اسم المحل',
                commercial_register='رقم السجل التجاري',
                tax_number='رقم البطاقة الضريبية'
            )
        return settings


class Manufacturer(models.Model):
    name = models.CharField(_('اسم الشركة المصنعة'), max_length=100)
    country = models.CharField(_('بلد المنشأ'), max_length=100, blank=True, null=True)
    website = models.URLField(_('الموقع الإلكتروني'), blank=True, null=True)
    logo = models.ImageField(_('الشعار'), upload_to='manufacturers/', blank=True, null=True)
    description = models.TextField(_('الوصف'), blank=True, null=True)
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاريخ التحديث'), auto_now=True)

    class Meta:
        verbose_name = _('شركة مصنعة')
        verbose_name_plural = _('الشركات المصنعة')
        ordering = ['name']

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(_('اسم الفئة'), max_length=100)
    description = models.TextField(_('الوصف'), blank=True, null=True)
    parent = models.ForeignKey('self', verbose_name=_('الفئة الأم'), on_delete=models.CASCADE, blank=True, null=True, related_name='children')
    image = models.ImageField(_('الصورة'), upload_to='categories/', blank=True, null=True)
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاريخ التحديث'), auto_now=True)

    class Meta:
        verbose_name = _('فئة')
        verbose_name_plural = _('الفئات')
        ordering = ['name']

    def __str__(self):
        return self.name


class CarModel(models.Model):
    name = models.CharField(_('اسم الموديل'), max_length=100)
    manufacturer = models.ForeignKey(Manufacturer, verbose_name=_('الشركة المصنعة'), on_delete=models.CASCADE, related_name='car_models')
    year_from = models.PositiveIntegerField(_('سنة البداية'))
    year_to = models.PositiveIntegerField(_('سنة النهاية'), blank=True, null=True)
    image = models.ImageField(_('الصورة'), upload_to='car_models/', blank=True, null=True)
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاريخ التحديث'), auto_now=True)

    class Meta:
        verbose_name = _('موديل سيارة')
        verbose_name_plural = _('موديلات السيارات')
        ordering = ['manufacturer', 'name']

    def __str__(self):
        return f"{self.manufacturer.name} {self.name} ({self.year_from}-{self.year_to or 'حتى الآن'})"


class Part(models.Model):
    CONDITION_CHOICES = [
        ('new', _('جديد')),
        ('used', _('مستعمل')),
        ('refurbished', _('مجدد')),
    ]

    name = models.CharField(_('اسم القطعة'), max_length=200)
    part_number = models.CharField(_('رقم القطعة'), max_length=50, unique=True)
    category = models.ForeignKey(Category, verbose_name=_('الفئة'), on_delete=models.CASCADE, related_name='parts')
    manufacturer = models.ForeignKey(Manufacturer, verbose_name=_('الشركة المصنعة'), on_delete=models.CASCADE, related_name='parts')
    compatible_cars = models.ManyToManyField(CarModel, verbose_name=_('السيارات المتوافقة'), related_name='compatible_parts', blank=True)
    description = models.TextField(_('الوصف'), blank=True, null=True)
    condition = models.CharField(_('الحالة'), max_length=20, choices=CONDITION_CHOICES, default='new')
    price = models.DecimalField(_('سعر البيع'), max_digits=10, decimal_places=2)
    purchase_price = models.DecimalField(_('سعر الشراء'), max_digits=10, decimal_places=2, default=0)
    stock_quantity = models.PositiveIntegerField(_('الكمية المتوفرة'))
    min_stock_level = models.PositiveIntegerField(_('الحد الأدنى للمخزون'), default=5)
    location = models.CharField(_('موقع التخزين'), max_length=100, blank=True, null=True)
    weight = models.DecimalField(_('الوزن (كجم)'), max_digits=6, decimal_places=2, blank=True, null=True)
    dimensions = models.CharField(_('الأبعاد'), max_length=100, blank=True, null=True)
    image = models.ImageField(_('الصورة'), upload_to='parts/', blank=True, null=True)
    is_active = models.BooleanField(_('نشط'), default=True)
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاريخ التحديث'), auto_now=True)

    class Meta:
        verbose_name = _('قطعة غيار')
        verbose_name_plural = _('قطع الغيار')
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.part_number})"

    @property
    def is_low_stock(self):
        return self.stock_quantity <= self.min_stock_level


class Supplier(models.Model):
    name = models.CharField(_('اسم المورد'), max_length=100)
    tax_number = models.CharField(_('الرقم الضريبي'), max_length=50, blank=True, null=True)
    contact_person = models.CharField(_('الشخص المسؤول'), max_length=100, blank=True, null=True)
    email = models.EmailField(_('البريد الإلكتروني'), blank=True, null=True)
    phone = models.CharField(_('رقم الهاتف'), max_length=20, blank=True, null=True)
    address = models.TextField(_('العنوان'), blank=True, null=True)
    website = models.URLField(_('الموقع الإلكتروني'), blank=True, null=True)
    notes = models.TextField(_('ملاحظات'), blank=True, null=True)
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاريخ التحديث'), auto_now=True)

    class Meta:
        verbose_name = _('مورد')
        verbose_name_plural = _('الموردين')
        ordering = ['name']

    def __str__(self):
        return self.name


class Purchase(models.Model):
    STATUS_CHOICES = [
        ('pending', _('قيد الانتظار')),
        ('ordered', _('تم الطلب')),
        ('received', _('تم الاستلام')),
        ('cancelled', _('ملغي')),
    ]

    supplier = models.ForeignKey(Supplier, verbose_name=_('المورد'), on_delete=models.CASCADE, related_name='purchases')
    purchase_date = models.DateField(_('تاريخ الشراء'))
    expected_delivery = models.DateField(_('تاريخ التسليم المتوقع'), blank=True, null=True)
    actual_delivery = models.DateField(_('تاريخ التسليم الفعلي'), blank=True, null=True)
    status = models.CharField(_('الحالة'), max_length=20, choices=STATUS_CHOICES, default='pending')
    invoice_number = models.CharField(_('رقم الفاتورة'), max_length=50, blank=True, null=True)
    total_amount = models.DecimalField(_('المبلغ الإجمالي'), max_digits=10, decimal_places=2)
    notes = models.TextField(_('ملاحظات'), blank=True, null=True)
    created_by = models.ForeignKey(User, verbose_name=_('تم الإنشاء بواسطة'), on_delete=models.SET_NULL, null=True, related_name='created_purchases')
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاريخ التحديث'), auto_now=True)

    class Meta:
        verbose_name = _('عملية شراء')
        verbose_name_plural = _('عمليات الشراء')
        ordering = ['-purchase_date']

    def __str__(self):
        return f"{self.supplier.name} - {self.purchase_date} - {self.get_status_display()}"


class PurchaseItem(models.Model):
    purchase = models.ForeignKey(Purchase, verbose_name=_('عملية الشراء'), on_delete=models.CASCADE, related_name='items')
    part = models.ForeignKey(Part, verbose_name=_('قطعة الغيار'), on_delete=models.CASCADE, related_name='purchase_items')
    quantity = models.PositiveIntegerField(_('الكمية'))
    unit_price = models.DecimalField(_('سعر الوحدة'), max_digits=10, decimal_places=2)
    total_price = models.DecimalField(_('السعر الإجمالي'), max_digits=10, decimal_places=2)
    received_quantity = models.PositiveIntegerField(_('الكمية المستلمة'), default=0)
    notes = models.TextField(_('ملاحظات'), blank=True, null=True)

    class Meta:
        verbose_name = _('عنصر الشراء')
        verbose_name_plural = _('عناصر الشراء')

    def __str__(self):
        return f"{self.part.name} - {self.quantity} وحدة"

    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)


class Sale(models.Model):
    STATUS_CHOICES = [
        ('pending', _('قيد الانتظار')),
        ('completed', _('مكتمل')),
        ('cancelled', _('ملغي')),
    ]

    customer_name = models.CharField(_('اسم العميل'), max_length=100)
    customer_phone = models.CharField(_('رقم هاتف العميل'), max_length=20, blank=True, null=True)
    customer_email = models.EmailField(_('بريد العميل الإلكتروني'), blank=True, null=True)
    sale_date = models.DateTimeField(_('تاريخ البيع'))
    status = models.CharField(_('الحالة'), max_length=20, choices=STATUS_CHOICES, default='pending')
    invoice_number = models.CharField(_('رقم الفاتورة'), max_length=50, unique=True)
    total_amount = models.DecimalField(_('المبلغ الإجمالي'), max_digits=10, decimal_places=2)
    discount = models.DecimalField(_('الخصم'), max_digits=10, decimal_places=2, default=0)
    tax = models.DecimalField(_('الضريبة'), max_digits=10, decimal_places=2, default=0)
    final_amount = models.DecimalField(_('المبلغ النهائي'), max_digits=10, decimal_places=2)
    payment_method = models.CharField(_('طريقة الدفع'), max_length=50, blank=True, null=True)
    notes = models.TextField(_('ملاحظات'), blank=True, null=True)
    created_by = models.ForeignKey(User, verbose_name=_('تم الإنشاء بواسطة'), on_delete=models.SET_NULL, null=True, related_name='created_sales')
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاريخ التحديث'), auto_now=True)

    class Meta:
        verbose_name = _('عملية بيع')
        verbose_name_plural = _('عمليات البيع')
        ordering = ['-sale_date']

    def __str__(self):
        return f"{self.customer_name} - {self.invoice_number}"

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            # إنشاء رقم فاتورة تلقائي بتنسيق: INV-YYYYMMDD-XXXX
            from django.utils import timezone
            today = timezone.now().strftime('%Y%m%d')
            last_invoice = Sale.objects.filter(invoice_number__startswith=f'INV-{today}').order_by('-invoice_number').first()
            if last_invoice:
                last_number = int(last_invoice.invoice_number.split('-')[-1])
                new_number = str(last_number + 1).zfill(4)
            else:
                new_number = '0001'
            self.invoice_number = f'INV-{today}-{new_number}'
        
        # التحقق من القيم وتعيين القيم الافتراضية إذا كانت فارغة
        if self.total_amount is None:
            self.total_amount = 0
        if self.discount is None:
            self.discount = 0
        if self.tax is None:
            self.tax = 0
            
        self.final_amount = self.total_amount - self.discount + self.tax
        super().save(*args, **kwargs)


class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, verbose_name=_('عملية البيع'), on_delete=models.CASCADE, related_name='items')
    part = models.ForeignKey(Part, verbose_name=_('قطعة الغيار'), on_delete=models.CASCADE, related_name='sale_items')
    quantity = models.PositiveIntegerField(_('الكمية'))
    unit_price = models.DecimalField(_('سعر الوحدة'), max_digits=10, decimal_places=2)
    total_price = models.DecimalField(_('السعر الإجمالي'), max_digits=10, decimal_places=2)
    notes = models.TextField(_('ملاحظات'), blank=True, null=True)

    class Meta:
        verbose_name = _('عنصر البيع')
        verbose_name_plural = _('عناصر البيع')

    def __str__(self):
        return f"{self.part.name} - {self.quantity} وحدة"

    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)


class Inventory(models.Model):
    part = models.OneToOneField(Part, verbose_name=_('قطعة الغيار'), on_delete=models.CASCADE, related_name='inventory')
    last_stock_update = models.DateTimeField(_('آخر تحديث للمخزون'), auto_now=True)
    last_inventory_check = models.DateTimeField(_('آخر جرد للمخزون'), blank=True, null=True)
    notes = models.TextField(_('ملاحظات'), blank=True, null=True)

    class Meta:
        verbose_name = _('مخزون')
        verbose_name_plural = _('المخزون')

    def __str__(self):
        return f"مخزون {self.part.name}"


class ShopInfo(models.Model):
    name = models.CharField(_('اسم المحل'), max_length=200)
    logo = models.ImageField(_('شعار المحل'), upload_to='shop/', blank=True, null=True)
    address = models.TextField(_('عنوان المحل'))
    phone = models.CharField(_('رقم الهاتف'), max_length=20)
    mobile = models.CharField(_('رقم الجوال'), max_length=20, blank=True, null=True)
    email = models.EmailField(_('البريد الإلكتروني'), blank=True, null=True)
    website = models.URLField(_('الموقع الإلكتروني'), blank=True, null=True)
    tax_number = models.CharField(_('الرقم الضريبي'), max_length=50)
    commercial_register = models.CharField(_('رقم السجل التجاري'), max_length=50)
    commercial_register_date = models.DateField(_('تاريخ السجل التجاري'))
    tax_certificate = models.FileField(_('شهادة التسجيل الضريبي'), upload_to='shop/documents/', blank=True, null=True)
    commercial_register_document = models.FileField(_('وثيقة السجل التجاري'), upload_to='shop/documents/', blank=True, null=True)
    bank_name = models.CharField(_('اسم البنك'), max_length=100, blank=True, null=True)
    bank_account = models.CharField(_('رقم الحساب البنكي'), max_length=50, blank=True, null=True)
    iban = models.CharField(_('رقم الآيبان'), max_length=50, blank=True, null=True)
    swift_code = models.CharField(_('رمز السويفت'), max_length=20, blank=True, null=True)
    notes = models.TextField(_('ملاحظات إضافية'), blank=True, null=True)
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاريخ التحديث'), auto_now=True)

    class Meta:
        verbose_name = _('معلومات المحل')
        verbose_name_plural = _('معلومات المحل')

    def __str__(self):
        return self.name
        
    @classmethod
    def get_default(cls):
        """الحصول على معلومات المحل الافتراضية أو إنشاء سجل جديد إذا لم يكن موجودًا"""
        shop_info, created = cls.objects.get_or_create(pk=1, defaults={
            'name': 'اسم المحل',
            'address': 'عنوان المحل',
            'phone': '000000000',
            'tax_number': '000000000',
            'commercial_register': '000000000',
            'commercial_register_date': '2023-01-01',
        })
        return shop_info