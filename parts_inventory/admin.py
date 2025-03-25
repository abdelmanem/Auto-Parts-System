from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import (
    Manufacturer, Category, CarModel, Part,
    Supplier, Purchase, PurchaseItem,
    Sale, SaleItem, ShopInfo
)


@admin.register(Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'website')
    search_fields = ('name', 'country')
    list_filter = ('country',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent')
    search_fields = ('name',)
    list_filter = ('parent',)


@admin.register(CarModel)
class CarModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'manufacturer', 'year_from', 'year_to')
    search_fields = ('name', 'manufacturer__name')
    list_filter = ('manufacturer', 'year_from')


class PurchaseItemInline(admin.TabularInline):
    model = PurchaseItem
    extra = 1


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ('supplier', 'purchase_date', 'status', 'total_amount')
    search_fields = ('supplier__name', 'invoice_number')
    list_filter = ('status', 'purchase_date')
    inlines = [PurchaseItemInline]


class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 1


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'sale_date', 'status', 'final_amount')
    search_fields = ('customer_name', 'invoice_number')
    list_filter = ('status', 'sale_date')
    inlines = [SaleItemInline]


@admin.register(Part)
class PartAdmin(admin.ModelAdmin):
    list_display = ('name', 'part_number', 'category', 'manufacturer', 'price', 'stock_quantity', 'is_low_stock', 'is_active')
    search_fields = ('name', 'part_number')
    list_filter = ('category', 'manufacturer', 'condition', 'is_active')
    filter_horizontal = ('compatible_cars',)


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_person', 'email', 'phone')
    search_fields = ('name', 'contact_person')


@admin.register(ShopInfo)
class ShopInfoAdmin(admin.ModelAdmin):
    list_display = ('name', 'tax_number', 'commercial_register', 'phone', 'email')
    fieldsets = (
        (_('معلومات المحل الأساسية'), {
            'fields': ('name', 'logo', 'address', 'phone', 'mobile', 'email', 'website')
        }),
        (_('معلومات قانونية'), {
            'fields': ('tax_number', 'commercial_register', 'commercial_register_date', 
                      'tax_certificate', 'commercial_register_document')
        }),
        (_('معلومات بنكية'), {
            'fields': ('bank_name', 'bank_account', 'iban', 'swift_code')
        }),
        (_('معلومات إضافية'), {
            'fields': ('notes',)
        }),
    )
    
    def has_add_permission(self, request):
        # التحقق من وجود سجل واحد فقط
        return ShopInfo.objects.count() == 0
        
    def has_delete_permission(self, request, obj=None):
        # منع حذف السجل
        return False