from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from parts_inventory.models import Part

class InventoryMovement(models.Model):
    MOVEMENT_TYPES = [
        ('sale', _('بيع')),
        ('purchase', _('شراء')),
        ('adjustment_add', _('إضافة يدوية')),
        ('adjustment_subtract', _('خصم يدوي')),
        ('return_in', _('مرتجع وارد')),
        ('return_out', _('مرتجع صادر')),
    ]

    part = models.ForeignKey(Part, verbose_name=_('قطعة الغيار'), on_delete=models.CASCADE, related_name='inventory_movements')
    movement_type = models.CharField(_('نوع الحركة'), max_length=20, choices=MOVEMENT_TYPES)
    quantity = models.IntegerField(_('الكمية'))
    previous_quantity = models.IntegerField(_('الكمية السابقة'))
    current_quantity = models.IntegerField(_('الكمية الحالية'))
    unit_price = models.DecimalField(_('سعر الوحدة'), max_digits=10, decimal_places=2)
    total_price = models.DecimalField(_('السعر الإجمالي'), max_digits=10, decimal_places=2)
    reference_number = models.CharField(_('رقم المرجع'), max_length=50, blank=True, null=True)
    reference_type = models.CharField(_('نوع المرجع'), max_length=20, blank=True, null=True)
    notes = models.TextField(_('ملاحظات'), blank=True, null=True)
    created_by = models.ForeignKey(User, verbose_name=_('تم الإنشاء بواسطة'), on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)

    class Meta:
        verbose_name = _('حركة مخزون')
        verbose_name_plural = _('حركات المخزون')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_movement_type_display()} - {self.part.name} - {self.quantity}"

    def save(self, *args, **kwargs):
        if not self.pk:  # Only for new records
            self.previous_quantity = self.part.stock_quantity
            if self.movement_type in ['sale', 'adjustment_subtract', 'return_out']:
                self.current_quantity = self.previous_quantity - abs(self.quantity)
            else:
                self.current_quantity = self.previous_quantity + abs(self.quantity)
            
            # Update part stock quantity
            self.part.stock_quantity = self.current_quantity
            self.part.save()
            
            # Calculate total price
            self.total_price = self.quantity * self.unit_price
            
        super().save(*args, **kwargs)