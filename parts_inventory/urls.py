from django.urls import path, include
from . import views

app_name = 'parts_inventory'

urlpatterns = [
    path('', views.index, name='index'),
    # قطع الغيار
    path('parts/', views.parts_list, name='parts_list'),
    path('parts/add/', views.part_form, name='part_form'),
    path('parts/<int:pk>/', views.part_detail, name='part_detail'),
    path('parts/<int:pk>/edit/', views.part_form, name='part_edit'),
    # الموردين
    path('suppliers/', views.suppliers_list, name='suppliers_list'),
    path('suppliers/add/', views.supplier_form, name='supplier_form'),
    path('suppliers/<int:pk>/', views.supplier_detail, name='supplier_detail'),
    path('suppliers/<int:pk>/edit/', views.supplier_form, name='supplier_edit'),
    # المبيعات
    path('sales/', views.sales_list, name='sales_list'),
    path('sales/add/', views.sale_form, name='sale_form'),
    path('sales/<int:pk>/', views.sale_detail, name='sale_detail'),
    path('sales/<int:pk>/edit/', views.sale_form, name='sale_edit'),
    # المشتريات
    path('purchases/', views.purchases_list, name='purchases_list'),
    path('purchases/add/', views.purchase_form, name='purchase_form'),
    path('purchases/<int:pk>/', views.purchase_detail, name='purchase_detail'),
    path('purchases/<int:pk>/edit/', views.purchase_form, name='purchase_edit'),
    
    # الشركات المصنعة
    path('manufacturers/create/', views.manufacturer_create_ajax, name='manufacturer_create_ajax'),
    
    # الفئات
    path('categories/create/', views.category_create_ajax, name='category_create_ajax'),
    
    # المسارات المالية
    path('financial/', include('parts_inventory.financial.urls')),
    
    # الإعدادات
    path('settings/shop/', views.shop_settings, name='shop_settings'),
    path('settings/system/', views.shop_settings, name='system_settings'),
    path('manufacturers/', views.manufacturers_list, name='manufacturers_list'),
    path('manufacturers/create/', views.manufacturer_form, name='manufacturer_create'),
    path('manufacturers/<int:pk>/edit/', views.manufacturer_form, name='manufacturer_update'),
    path('manufacturers/<int:pk>/delete/', views.manufacturer_delete, name='manufacturer_delete'),
    path('categories/', views.categories_list, name='categories_list'),
]