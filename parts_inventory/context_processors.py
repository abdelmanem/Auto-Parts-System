from django.utils import timezone
from .models import ShopInfo

def current_year(request):
    """إضافة السنة الحالية إلى سياق القالب"""
    return {'current_year': timezone.now().year}

def shop_info(request):
    """إضافة معلومات المحل إلى سياق القالب"""
    try:
        info = ShopInfo.get_default()
        return {'shop_info': info}
    except Exception:
        return {'shop_info': None}