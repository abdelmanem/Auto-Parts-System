from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from .models import License

@receiver(pre_save, sender=License)
def validate_license_dates(sender, instance, **kwargs):
    """التحقق من صحة تواريخ الترخيص قبل الحفظ"""
    if instance.start_date and instance.end_date:
        if instance.start_date > instance.end_date:
            raise ValueError('تاريخ انتهاء الترخيص يجب أن يكون بعد تاريخ البداية')

@receiver(post_save, sender=License)
def send_license_notifications(sender, instance, created, **kwargs):
    """إرسال إشعارات عن حالة الترخيص"""
    if created:
        # إرسال بريد إلكتروني عند إنشاء ترخيص جديد
        subject = 'تم إنشاء ترخيص جديد'
        message = f'تم إنشاء ترخيص جديد لشركة {instance.company_name}\n'
        message += f'مفتاح الترخيص: {instance.license_key}\n'
        message += f'تاريخ البداية: {instance.start_date}\n'
        message += f'تاريخ الانتهاء: {instance.end_date}'
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [instance.contact_email],
            fail_silently=True,
        )
    
    # التحقق من قرب انتهاء الترخيص
    days_remaining = instance.days_until_expiry()
    if days_remaining <= 30 and instance.is_active:
        subject = 'تنبيه: اقتراب انتهاء الترخيص'
        message = f'تنبيه: ترخيص شركة {instance.company_name} سينتهي خلال {days_remaining} يوم.\n'
        message += 'يرجى تجديد الترخيص قبل انتهاء المدة.'
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [instance.contact_email],
            fail_silently=True,
        )