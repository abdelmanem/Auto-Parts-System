from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from django.contrib import messages
from django.utils.translation import gettext as _
from .models import License

class LicenseMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # استثناء صفحات معينة من التحقق من الترخيص
        exempt_paths = [
            reverse('admin:index'),
            reverse('admin:login'),
            '/static/',
            '/media/'
        ]

        # التحقق مما إذا كان المسار الحالي معفى
        if any(request.path.startswith(path) for path in exempt_paths):
            return self.get_response(request)

        try:
            # البحث عن ترخيص نشط
            license = License.objects.filter(
                is_active=True,
                start_date__lte=timezone.now().date(),
                end_date__gte=timezone.now().date()
            ).first()

            if not license:
                messages.error(
                    request,
                    _('لا يوجد ترخيص نشط للنظام. يرجى الاتصال بالمسؤول.')
                )
                return redirect('admin:index')

            # التحقق من قرب انتهاء الترخيص
            days_remaining = license.days_until_expiry()
            if days_remaining <= 7:
                messages.warning(
                    request,
                    _('تنبيه: سينتهي الترخيص خلال {} أيام. يرجى تجديد الترخيص.').format(days_remaining)
                )

        except Exception as e:
            messages.error(
                request,
                _('حدث خطأ في التحقق من الترخيص. يرجى الاتصال بالمسؤول.')
            )
            return redirect('admin:index')

        return self.get_response(request)