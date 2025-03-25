from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

class License(models.Model):
    license_key = models.CharField(_('مفتاح الترخيص'), max_length=50, unique=True)
    company_name = models.CharField(_('اسم الشركة'), max_length=100)
    contact_email = models.EmailField(_('البريد الإلكتروني للتواصل'))
    start_date = models.DateField(_('تاريخ بداية الترخيص'))
    end_date = models.DateField(_('تاريخ انتهاء الترخيص'))
    is_active = models.BooleanField(_('نشط'), default=True)
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاريخ التحديث'), auto_now=True)
    created_by = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_licenses',
        verbose_name=_('تم الإنشاء بواسطة')
    )

    class Meta:
        verbose_name = _('ترخيص')
        verbose_name_plural = _('التراخيص')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.company_name} - {self.license_key}'

    def clean(self):
        if self.start_date and self.end_date:
            if self.start_date > self.end_date:
                raise ValidationError({
                    'end_date': _('تاريخ الانتهاء يجب أن يكون بعد تاريخ البداية')
                })

    def is_expired(self):
        return timezone.now().date() > self.end_date

    def days_until_expiry(self):
        if self.is_expired():
            return 0
        return (self.end_date - timezone.now().date()).days