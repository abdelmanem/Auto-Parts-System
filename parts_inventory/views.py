from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum, Count, F
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.forms import modelform_factory
from .models import (
    Manufacturer, Category, CarModel, Part,
    Supplier, Purchase, PurchaseItem,
    Sale, SaleItem, Inventory
)
from .forms import PartForm


@login_required
def index(request):
    """عرض الصفحة الرئيسية"""
    # إحصائيات عامة
    total_parts = Part.objects.count()
    low_stock_parts = Part.objects.filter(stock_quantity__lte=F('min_stock_level')).count()
    total_manufacturers = Manufacturer.objects.count()
    total_suppliers = Supplier.objects.count()
    
    # آخر المبيعات
    recent_sales = Sale.objects.order_by('-sale_date')[:5]
    
    # آخر المشتريات
    recent_purchases = Purchase.objects.order_by('-purchase_date')[:5]
    
    context = {
        'total_parts': total_parts,
        'low_stock_parts': low_stock_parts,
        'total_manufacturers': total_manufacturers,
        'total_suppliers': total_suppliers,
        'recent_sales': recent_sales,
        'recent_purchases': recent_purchases,
    }
    
    return render(request, 'parts_inventory/index.html', context)


@login_required
def parts_list(request):
    """عرض قائمة قطع الغيار"""
    query = request.GET.get('q', '')
    category_id = request.GET.get('category', '')
    manufacturer_id = request.GET.get('manufacturer', '')
    condition = request.GET.get('condition', '')
    
    parts = Part.objects.all()
    
    # تطبيق الفلاتر
    if query:
        parts = parts.filter(
            Q(name__icontains=query) | 
            Q(part_number__icontains=query) | 
            Q(description__icontains=query)
        )
    
    if category_id:
        parts = parts.filter(category_id=category_id)
    
    if manufacturer_id:
        parts = parts.filter(manufacturer_id=manufacturer_id)
    
    if condition:
        parts = parts.filter(condition=condition)
        
    # فلترة المخزون المنخفض
    stock_status = request.GET.get('stock_status', '')
    if stock_status == 'low':
        parts = parts.filter(stock_quantity__lte=F('min_stock_level'))
    elif stock_status == 'normal':
        parts = parts.filter(stock_quantity__gt=F('min_stock_level'))
    
    # الترتيب
    sort_by = request.GET.get('sort', 'name')
    if sort_by.startswith('-'):
        sort_field = sort_by[1:]
        parts = parts.order_by(sort_by)
    else:
        sort_field = sort_by
        parts = parts.order_by(sort_by)
    
    # التصفح
    paginator = Paginator(parts, 20)  # 20 قطعة في الصفحة
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # البيانات للفلاتر
    categories = Category.objects.all()
    manufacturers = Manufacturer.objects.all()
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'manufacturers': manufacturers,
        'query': query,
        'selected_category': category_id,
        'selected_manufacturer': manufacturer_id,
        'selected_condition': condition,
        'sort_by': sort_by,
        'sort_field': sort_field,
    }
    
    return render(request, 'parts_inventory/parts_list.html', context)


@login_required
def part_detail(request, pk):
    """عرض تفاصيل قطعة غيار"""
    part = get_object_or_404(Part, pk=pk)
    
    # تاريخ المبيعات
    sales_history = SaleItem.objects.filter(part=part).order_by('-sale__sale_date')
    
    # تاريخ المشتريات
    purchase_history = PurchaseItem.objects.filter(part=part).order_by('-purchase__purchase_date')
    
    context = {
        'part': part,
        'sales_history': sales_history,
        'purchase_history': purchase_history,
    }
    
    return render(request, 'parts_inventory/part_detail.html', context)


@login_required
def suppliers_list(request):
    """عرض قائمة الموردين"""
    query = request.GET.get('q', '')
    
    suppliers = Supplier.objects.all()
    
    if query:
        suppliers = suppliers.filter(
            Q(name__icontains=query) | 
            Q(contact_person__icontains=query) | 
            Q(email__icontains=query) | 
            Q(phone__icontains=query)
        )
    
    # الترتيب
    sort_by = request.GET.get('sort', 'name')
    suppliers = suppliers.order_by(sort_by)
    
    # التصفح
    paginator = Paginator(suppliers, 20)  # 20 مورد في الصفحة
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'query': query,
        'sort_by': sort_by,
    }
    
    return render(request, 'parts_inventory/suppliers_list.html', context)


@login_required
def supplier_detail(request, pk):
    """عرض تفاصيل مورد"""
    supplier = get_object_or_404(Supplier, pk=pk)
    
    # تاريخ المشتريات
    purchases = Purchase.objects.filter(supplier=supplier).order_by('-purchase_date')
    
    # حساب عدد عمليات الشراء لكل حالة
    pending_count = purchases.filter(status='pending').count()
    ordered_count = purchases.filter(status='ordered').count()
    received_count = purchases.filter(status='received').count()
    
    context = {
        'supplier': supplier,
        'purchases': purchases,
        'pending_count': pending_count,
        'ordered_count': ordered_count,
        'received_count': received_count,
    }
    
    return render(request, 'parts_inventory/supplier_detail.html', context)


@login_required
def manufacturers_list(request):
    """عرض قائمة الشركات المصنعة"""
    query = request.GET.get('q', '')
    
    manufacturers = Manufacturer.objects.all()
    
    if query:
        manufacturers = manufacturers.filter(
            Q(name__icontains=query) | 
            Q(country__icontains=query)
        )
    
    # الترتيب
    sort_by = request.GET.get('sort', 'name')
    manufacturers = manufacturers.order_by(sort_by)
    
    # التصفح
    paginator = Paginator(manufacturers, 20)  # 20 شركة في الصفحة
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'manufacturers': page_obj,
        'query': query,
        'sort_by': sort_by,
    }
    
    return render(request, 'parts_inventory/manufacturer_list.html', context)


@login_required
def sales_list(request):
    """عرض قائمة المبيعات"""
    query = request.GET.get('q', '')
    status = request.GET.get('status', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    sales = Sale.objects.all()
    
    if query:
        sales = sales.filter(
            Q(customer_name__icontains=query) | 
            Q(invoice_number__icontains=query)
        )
    
    if status:
        sales = sales.filter(status=status)
    
    if date_from:
        sales = sales.filter(sale_date__gte=date_from)
    
    if date_to:
        sales = sales.filter(sale_date__lte=date_to)
    
    # الترتيب
    sort_by = request.GET.get('sort', '-sale_date')
    sales = sales.order_by(sort_by)
    
    # التصفح
    paginator = Paginator(sales, 20)  # 20 عملية بيع في الصفحة
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'query': query,
        'selected_status': status,
        'date_from': date_from,
        'date_to': date_to,
        'sort_by': sort_by,
    }
    
    return render(request, 'parts_inventory/sales_list.html', context)


@login_required
def sale_detail(request, pk):
    """عرض تفاصيل عملية بيع"""
    sale = get_object_or_404(Sale, pk=pk)
    
    # عناصر البيع
    items = sale.items.all()
    
    context = {
        'sale': sale,
        'items': items,
    }
    
    return render(request, 'parts_inventory/sale_detail.html', context)


@login_required
def purchases_list(request):
    """عرض قائمة المشتريات"""
    query = request.GET.get('q', '')
    status = request.GET.get('status', '')
    supplier_id = request.GET.get('supplier', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    purchases = Purchase.objects.all()
    
    if query:
        purchases = purchases.filter(
            Q(invoice_number__icontains=query)
        )
    
    if status:
        purchases = purchases.filter(status=status)
    
    if supplier_id:
        purchases = purchases.filter(supplier_id=supplier_id)
    
    if date_from:
        purchases = purchases.filter(purchase_date__gte=date_from)
    
    if date_to:
        purchases = purchases.filter(purchase_date__lte=date_to)
    
    # الترتيب
    sort_by = request.GET.get('sort', '-purchase_date')
    purchases = purchases.order_by(sort_by)
    
    # التصفح
    paginator = Paginator(purchases, 20)  # 20 عملية شراء في الصفحة
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # البيانات للفلاتر
    suppliers = Supplier.objects.all()
    
    context = {
        'page_obj': page_obj,
        'suppliers': suppliers,
        'query': query,
        'selected_status': status,
        'selected_supplier': supplier_id,
        'date_from': date_from,
        'date_to': date_to,
        'sort_by': sort_by,
    }
    
    return render(request, 'parts_inventory/purchases_list.html', context)


@login_required
def purchase_detail(request, pk):
    """عرض تفاصيل عملية شراء"""
    purchase = get_object_or_404(Purchase, pk=pk)
    
    # عناصر الشراء
    items = purchase.items.all()
    
    context = {
        'purchase': purchase,
        'items': items,
    }
    
    return render(request, 'parts_inventory/purchase_detail.html', context)


@login_required
def part_form(request, pk=None):
    """نموذج إضافة/تعديل قطعة غيار"""
    part = None if pk is None else get_object_or_404(Part, pk=pk)
    
    # تحديد القالب المناسب بناءً على نوع العملية (إضافة/تعديل)
    template_name = 'parts_inventory/part_edit.html' if pk else 'parts_inventory/part_form.html'
    
    if request.method == 'GET':
        form = PartForm(instance=part) if part else PartForm()
    elif request.method == 'POST':
        form = PartForm(request.POST, request.FILES, instance=part)
    
    if request.method == 'POST':
        form = PartForm(request.POST, request.FILES, instance=part)
        if form.is_valid():
            try:
                part = form.save(commit=False)
                # التحقق من صحة البيانات
                if part.stock_quantity < 0:
                    messages.error(request, 'الكمية المتوفرة يجب أن تكون أكبر من أو تساوي صفر')
                    raise ValueError('الكمية المتوفرة غير صالحة')
                if part.price <= 0:
                    messages.error(request, 'سعر البيع يجب أن يكون أكبر من صفر')
                    raise ValueError('سعر البيع غير صالح')
                if part.purchase_price < 0:
                    messages.error(request, 'سعر الشراء يجب أن يكون أكبر من أو يساوي صفر')
                    raise ValueError('سعر الشراء غير صالح')
                if part.min_stock_level < 0:
                    messages.error(request, 'الحد الأدنى للمخزون يجب أن يكون أكبر من أو يساوي صفر')
                    raise ValueError('الحد الأدنى للمخزون غير صالح')
                
                part.save()
                form.save_m2m()  # حفظ العلاقات متعددة-متعددة
                messages.success(request, 'تم حفظ قطعة الغيار بنجاح')
                return redirect('parts_inventory:parts_list')
            except ValueError as ve:
                messages.error(request, str(ve))
            except Exception as e:
                messages.error(request, f'حدث خطأ أثناء حفظ قطعة الغيار: {str(e)}')
        else:
            # عرض أخطاء محددة للحقول
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'خطأ في {form.fields[field].label}: {error}')
    else:
        # تحميل بيانات القطعة في النموذج إذا كانت موجودة
        form = PartForm(instance=part)
        if part:
            # تحديث عنوان الصفحة للتعديل
            context = {
                'form': form,
                'part': part,
                'manufacturers': Manufacturer.objects.all(),
                'categories': Category.objects.all(),
                'car_models': CarModel.objects.all(),
                'is_edit': True,
                'page_title': f'تعديل قطعة الغيار - {part.name}'
            }
        else:
            context = {
                'form': form,
                'manufacturers': Manufacturer.objects.all(),
                'categories': Category.objects.all(),
                'car_models': CarModel.objects.all(),
                'is_edit': False,
                'page_title': 'إضافة قطعة غيار جديدة'
            }
        return render(request, template_name, context)
    
    context = {
        'form': form,
        'part': part,
        'manufacturers': Manufacturer.objects.all(),
        'categories': Category.objects.all(),
        'car_models': CarModel.objects.all(),
    }
    
    return render(request, template_name, context)

@login_required
def manufacturer_delete(request, pk):
    """حذف شركة مصنعة"""
    manufacturer = get_object_or_404(Manufacturer, pk=pk)
    try:
        manufacturer.delete()
        messages.success(request, 'تم حذف الشركة المصنعة بنجاح')
    except Exception as e:
        messages.error(request, 'حدث خطأ أثناء حذف الشركة المصنعة')
    return redirect('parts_inventory:manufacturers_list')

@login_required
def manufacturer_create_ajax(request):
    """إضافة شركة مصنعة جديدة عبر AJAX"""
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            # التحقق من وجود الاسم
            name = request.POST.get('name')
            if not name:
                return JsonResponse({
                    'success': False,
                    'error': 'اسم الشركة المصنعة مطلوب'
                })

            # التحقق من عدم تكرار الاسم
            if Manufacturer.objects.filter(name=name).exists():
                return JsonResponse({
                    'success': False,
                    'error': 'يوجد شركة مصنعة بهذا الاسم بالفعل'
                })

            # إنشاء شركة مصنعة جديدة
            manufacturer = Manufacturer.objects.create(
                name=name,
                country=request.POST.get('country'),
                website=request.POST.get('website'),
                description=request.POST.get('description')
            )
            
            # إرجاع البيانات كـ JSON
            return JsonResponse({
                'success': True,
                'manufacturer': {
                    'id': manufacturer.id,
                    'name': manufacturer.name
                }
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({
        'success': False,
        'error': 'طريقة الطلب غير مدعومة'
    })


@login_required
def category_create_ajax(request):
    """إضافة فئة جديدة عبر AJAX"""
    if request.method == 'POST':
        try:
            # التحقق من وجود الاسم
            name = request.POST.get('name')
            if not name:
                return JsonResponse({
                    'success': False,
                    'error': 'اسم الفئة مطلوب'
                })

            # التحقق من عدم تكرار الاسم
            if Category.objects.filter(name=name).exists():
                return JsonResponse({
                    'success': False,
                    'error': 'يوجد فئة بهذا الاسم بالفعل'
                })

            # إنشاء فئة جديدة
            category = Category.objects.create(
                name=name,
                description=request.POST.get('description'),
                parent_id=request.POST.get('parent')
            )
            
            # إرجاع البيانات كـ JSON
            return JsonResponse({
                'success': True,
                'category': {
                    'id': category.id,
                    'name': category.name
                }
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({
        'success': False,
        'error': 'طريقة الطلب غير مدعومة'
    })

@login_required
def supplier_form(request, pk=None):
    """نموذج إضافة/تعديل مورد"""
    supplier = None if pk is None else get_object_or_404(Supplier, pk=pk)
    template_name = 'parts_inventory/supplier_edit.html' if pk else 'parts_inventory/supplier_form.html'
    
    SupplierForm = modelform_factory(Supplier, fields=['name', 'contact_person', 'email', 'phone',
                                                      'address', 'tax_number'])
    
    if request.method == 'POST':
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تحديث بيانات المورد بنجاح' if pk else 'تم إضافة المورد بنجاح')
            return redirect('parts_inventory:suppliers_list')
    else:
        form = SupplierForm(instance=supplier)
    
    context = {
        'form': form,
        'supplier': supplier,
        'is_edit': pk is not None
    }
    
    return render(request, template_name, context)


@login_required
def sale_form(request, pk=None):
    """نموذج إضافة/تعديل عملية بيع"""
    sale = None if pk is None else get_object_or_404(Sale, pk=pk)
    
    SaleForm = modelform_factory(Sale, fields=['customer_name', 'invoice_number', 'sale_date',
                                              'payment_method', 'status', 'notes'])
    
    if request.method == 'POST':
        form = SaleForm(request.POST, instance=sale)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم حفظ عملية البيع بنجاح')
            return redirect('parts_inventory:sales_list')
    else:
        form = SaleForm(instance=sale)
    
    # جلب قطع الغيار المتوفرة في المخزون
    available_parts = Part.objects.filter(stock_quantity__gt=0).select_related('manufacturer')
    
    context = {
        'form': form,
        'sale': sale,
        'parts': available_parts,
    }
    
    return render(request, 'parts_inventory/sale_form.html', context)


@login_required
def purchase_form(request, pk=None):
    """نموذج إضافة/تعديل عملية شراء"""
    purchase = None if pk is None else get_object_or_404(Purchase, pk=pk)
    
    PurchaseForm = modelform_factory(Purchase, fields=['supplier', 'invoice_number', 'purchase_date',
                                                      'expected_delivery', 'status', 'notes'])
    
    if request.method == 'POST':
        form = PurchaseForm(request.POST, instance=purchase)
        if form.is_valid():
            try:
                # حفظ عملية الشراء
                purchase = form.save(commit=False)
                purchase.total_amount = float(request.POST.get('final_amount', 0))
                purchase.created_by = request.user
                purchase.save()
                
                # حفظ عناصر الشراء
                parts = request.POST.getlist('parts[]')
                quantities = request.POST.getlist('quantities[]')
                prices = request.POST.getlist('prices[]')
                
                for part_id, quantity, price in zip(parts, quantities, prices):
                    if part_id and quantity and price:
                        part = Part.objects.get(id=part_id)
                        PurchaseItem.objects.create(
                            purchase=purchase,
                            part=part,
                            quantity=int(quantity),
                            unit_price=float(price),
                            total_price=float(price) * int(quantity)
                        )
                
                messages.success(request, 'تم حفظ عملية الشراء بنجاح')
                return redirect('parts_inventory:purchases_list')
            except Exception as e:
                messages.error(request, f'حدث خطأ أثناء حفظ عملية الشراء: {str(e)}')
                return render(request, 'parts_inventory/purchase_form.html', {'form': form, 'purchase': purchase})

    else:
        form = PurchaseForm(instance=purchase)
    
    # إضافة قائمة الموردين إلى السياق
    suppliers = Supplier.objects.all()
    parts = Part.objects.filter(is_active=True)
    
    context = {
        'form': form,
        'purchase': purchase,
        'suppliers': suppliers,
        'parts': parts,
    }
    
    return render(request, 'parts_inventory/purchase_form.html', context)


@login_required
def shop_settings(request):
    """إعدادات المتجر"""
    # TODO: إضافة نموذج إعدادات المتجر
    context = {}
    return render(request, 'parts_inventory/store_settings_form.html', context)


@login_required
def manufacturer_form(request, pk=None):
    """نموذج إضافة/تعديل شركة مصنعة"""
    manufacturer = None if pk is None else get_object_or_404(Manufacturer, pk=pk)
    
    ManufacturerForm = modelform_factory(Manufacturer, fields=['name', 'country', 'website', 'description', 'logo'])
    
    if request.method == 'POST':
        form = ManufacturerForm(request.POST, request.FILES, instance=manufacturer)
        if form.is_valid():
            manufacturer = form.save()
            messages.success(request, 'تم حفظ الشركة المصنعة بنجاح')
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'manufacturer': {
                        'id': manufacturer.id,
                        'name': manufacturer.name,
                        'country': manufacturer.country,
                        'website': manufacturer.website,
                        'description': manufacturer.description
                    }
                })
            return redirect('parts_inventory:manufacturers_list')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'error': 'بيانات غير صالحة',
                    'errors': form.errors
                })
    else:
        form = ManufacturerForm(instance=manufacturer)
    
    context = {
        'form': form,
        'manufacturer': manufacturer,
    }
    
    return render(request, 'parts_inventory/manufacturer_form.html', context)


@login_required
def categories_list(request):
    """عرض قائمة الفئات"""
    query = request.GET.get('q', '')
    
    categories = Category.objects.all()
    
    if query:
        categories = categories.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query)
        )
    
    # الترتيب
    sort_by = request.GET.get('sort', 'name')
    categories = categories.order_by(sort_by)
    
    # التصفح
    paginator = Paginator(categories, 20)  # 20 فئة في الصفحة
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'query': query,
        'sort_by': sort_by,
    }
    
    return render(request, 'parts_inventory/categories_list.html', context)