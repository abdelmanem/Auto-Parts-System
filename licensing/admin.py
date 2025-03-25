from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import License

@admin.register(License)
class LicenseAdmin(admin.ModelAdmin):
    list_display = ['company_name', 'license_key', 'start_date', 'end_date', 'is_active', 'days_until_expiry']
    list_filter = ['is_active', 'start_date', 'end_date']
    search_fields = ['company_name', 'license_key', 'contact_email']
    readonly_fields = ['created_at', 'updated_at', 'created_by']
    fieldsets = [
        (_('معلومات الترخيص'), {
            'fields': ['license_key', 'company_name', 'contact_email']
        }),
        (_('تواريخ الترخيص'), {
            'fields': ['start_date', 'end_date', 'is_active']
        }),
        (_('معلومات النظام'), {
            'fields': ['created_at', 'updated_at', 'created_by'],
            'classes': ['collapse']
        })
    ]

    def save_model(self, request, obj, form, change):
        if not change:  # إذا كان هذا إنشاء جديد
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser  # فقط المسؤول يمكنه حذف التراخيص