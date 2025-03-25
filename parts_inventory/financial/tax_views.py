from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, Q, F
from django.utils import timezone
from django.core.paginator import Paginator
from datetime import datetime, timedelta
from decimal import Decimal
from django.http import HttpResponse
import json

from .tax_models import (
    TaxRate, TaxCategory, SaleTax, PurchaseTax, TaxReport
)
from parts_inventory.models import Sale, Purchase


@login_required
def tax_dashboard(request):
    """عرض لوحة تحكم الضرائب الرئيسية"""
    # إحصائيات عامة
    today = timezone.now().date()
    start_of_month = today.replace(day=1)
    
    # إجمالي ضرائب المبيعات للشهر الحالي
    current_month_sales_tax = SaleTax.objects.filter(
        sale__sale_date__date__gte=start_of_month,
        sale__sale_date__date__lte=today
    ).aggregate(Sum('tax_amount'))['tax_amount__sum'] or 0
    
    # إجمالي ضرائب المشتريات للشهر الحالي
    current_month_purchase_tax = PurchaseTax.objects.filter(
        purchase__purchase_date__gte=start_of_month,
        purchase__purchase_date__lte=today
    ).aggregate(Sum('tax_amount'))['tax_amount__sum'] or 0
    
    # ضرائب المبيعات غير المدفوعة
    unpaid_sales_tax = SaleTax.objects.filter(is_paid=False).aggregate(Sum('tax_amount'))['tax_amount__sum'] or 0
    
    # ضرائب المشتريات القابلة للخصم وغير المطالب بها
    unclaimed_purchase_tax = PurchaseTax.objects.filter(
        is_deductible=True, is_claimed=False
    ).aggregate(Sum('tax_amount'))['tax_amount__sum'] or 0
    
    # آخر التقارير الضريبية
    recent_tax_reports = TaxReport.objects.all().order_by('-end_date')[:5]
    
    # آخر ضرائب المبيعات
    recent_sales_taxes = SaleTax.objects.all().order_by('-created_at')[:5]
    
    # آخر ضرائب المشتريات
    recent_purchase_taxes = PurchaseTax.objects.all().order_by('-created_at')[:5]
    
    context = {
        'current_month_sales_tax': current_month_sales_tax,
        'current_month_purchase_tax': current_month_purchase_tax,
        'unpaid_sales_tax': unpaid_sales_tax,
        'unclaimed_purchase_tax': unclaimed_purchase_tax,
        'recent_tax_reports': recent_tax_reports,
        'recent_sales_taxes': recent_sales_taxes,
        'recent_purchase_taxes': recent_purchase_taxes,
        'tax_due': current_month_sales_tax - current_month_purchase_tax,
    }
    
    return render(request, 'parts_inventory/financial/tax_dashboard.html', context)


@login_required
def tax_rates_list(request):
    """عرض قائمة معدلات الضرائب"""
    tax_rates = TaxRate.objects.all()
    
    # تطبيق الفلاتر
    is_active = request.GET.get('is_active', '')
    is_default = request.GET.get('is_default', '')
    query = request.GET.get('q', '')
    
    if is_active != '':
        is_active_bool = is_active == 'true'
        tax_rates = tax_rates.filter(is_active=is_active_bool)
    
    if is_default != '':
        is_default_bool = is_default == 'true'
        tax_rates = tax_rates.filter(is_default=is_default_bool)
    
    if query:
        tax_rates = tax_rates.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query)
        )
    
    # الترتيب
    tax_rates = tax_rates.order_by('name')
    
    # التصفح
    paginator = Paginator(tax_rates, 20)  # 20 معدل ضريبة في الصفحة
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'is_active': is_active,
        'is_default': is_default,
        'query': query,
    }
    
    return render(request, 'parts_inventory/financial/tax_rates_list.html', context)


@login_required
def sales_taxes_list(request):
    """عرض قائمة ضرائب المبيعات"""
    sales_taxes = SaleTax.objects.all()
    
    # تطبيق الفلاتر
    is_paid = request.GET.get('is_paid', '')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
    query = request.GET.get('q', '')
    
    if is_paid != '':
        is_paid_bool = is_paid == 'true'
        sales_taxes = sales_taxes.filter(is_paid=is_paid_bool)
    
    if start_date:
        try:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            sales_taxes = sales_taxes.filter(sale__sale_date__date__gte=start_date_obj)
        except ValueError:
            pass
    
    if end_date:
        try:
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
            sales_taxes = sales_taxes.filter(sale__sale_date__date__lte=end_date_obj)
        except ValueError:
            pass
    
    if query:
        sales_taxes = sales_taxes.filter(
            Q(sale__invoice_number__icontains=query) | 
            Q(reference_number__icontains=query) | 
            Q(notes__icontains=query)
        )
    
    # الترتيب
    sales_taxes = sales_taxes.order_by('-sale__sale_date')
    
    # التصفح
    paginator = Paginator(sales_taxes, 20)  # 20 ضريبة في الصفحة
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # الحصول على عمليات البيع المتاحة لإضافة ضريبة
    available_sales = Sale.objects.filter(status='completed').order_by('-sale_date')[:100]
    
    # الحصول على معدلات الضريبة النشطة
    active_tax_rates = TaxRate.objects.filter(is_active=True).order_by('name')
    
    context = {
        'page_obj': page_obj,
        'is_paid': is_paid,
        'start_date': start_date,
        'end_date': end_date,
        'query': query,
        'available_sales': available_sales,
        'active_tax_rates': active_tax_rates,
    }
    
    return render(request, 'parts_inventory/financial/sales_taxes_list.html', context)


@login_required
def add_sales_tax(request):
    """إضافة ضريبة مبيعات جديدة"""
    if request.method == 'POST':
        # استخراج البيانات من النموذج
        sale_id = request.POST.get('sale')
        tax_rate_id = request.POST.get('tax_rate')
        tax_amount = request.POST.get('tax_amount')
        is_paid = 'is_paid' in request.POST
        payment_date = request.POST.get('payment_date') or None
        reference_number = request.POST.get('reference_number') or None
        notes = request.POST.get('notes') or None
        
        try:
            # التحقق من البيانات
            sale = Sale.objects.get(pk=sale_id)
            tax_rate = TaxRate.objects.get(pk=tax_rate_id)
            tax_amount = Decimal(tax_amount)
            
            # إنشاء ضريبة المبيعات
            sales_tax = SaleTax(
                sale=sale,
                tax_rate=tax_rate,
                tax_amount=tax_amount,
                is_paid=is_paid,
                reference_number=reference_number,
                notes=notes,
                created_by=request.user
            )
            
            # إذا تم تحديد أن الضريبة مدفوعة، نضيف تاريخ الدفع
            if is_paid and payment_date:
                try:
                    sales_tax.payment_date = datetime.strptime(payment_date, '%Y-%m-%d').date()
                except ValueError:
                    sales_tax.payment_date = timezone.now().date()
            
            sales_tax.save()
            messages.success(request, 'تم إضافة ضريبة المبيعات بنجاح')
            
        except Sale.DoesNotExist:
            messages.error(request, 'عملية البيع غير موجودة')
        except TaxRate.DoesNotExist:
            messages.error(request, 'معدل الضريبة غير موجود')
        except ValueError:
            messages.error(request, 'قيمة مبلغ الضريبة غير صالحة')
        except Exception as e:
            messages.error(request, f'حدث خطأ أثناء إضافة ضريبة المبيعات: {str(e)}')
    
    return redirect('parts_inventory:financial:sales_taxes_list')


@login_required
def purchase_taxes_list(request):
    """عرض قائمة ضرائب المشتريات"""
    purchase_taxes = PurchaseTax.objects.all()
    
    # تطبيق الفلاتر
    is_claimed = request.GET.get('is_claimed', '')
    is_deductible = request.GET.get('is_deductible', '')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
    query = request.GET.get('q', '')
    
    if is_claimed != '':
        is_claimed_bool = is_claimed == 'true'
        purchase_taxes = purchase_taxes.filter(is_claimed=is_claimed_bool)
    
    if is_deductible != '':
        is_deductible_bool = is_deductible == 'true'
        purchase_taxes = purchase_taxes.filter(is_deductible=is_deductible_bool)
    
    if start_date:
        try:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            purchase_taxes = purchase_taxes.filter(purchase__purchase_date__gte=start_date_obj)
        except ValueError:
            pass
    
    if end_date:
        try:
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
            purchase_taxes = purchase_taxes.filter(purchase__purchase_date__lte=end_date_obj)
        except ValueError:
            pass
    
    if query:
        purchase_taxes = purchase_taxes.filter(
            Q(purchase__reference_number__icontains=query) | 
            Q(reference_number__icontains=query) | 
            Q(notes__icontains=query)
        )
    
    # الترتيب
    purchase_taxes = purchase_taxes.order_by('-purchase__purchase_date')
    
    # التصفح
    paginator = Paginator(purchase_taxes, 20)  # 20 ضريبة في الصفحة
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'is_claimed': is_claimed,
        'is_deductible': is_deductible,
        'start_date': start_date,
        'end_date': end_date,
        'query': query,
    }
    
    return render(request, 'parts_inventory/financial/purchase_taxes_list.html', context)


@login_required
def tax_reports_list(request):
    """عرض قائمة التقارير الضريبية"""
    tax_reports = TaxReport.objects.all()
    
    # تطبيق الفلاتر
    report_type = request.GET.get('report_type', '')
    status = request.GET.get('status', '')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
    query = request.GET.get('q', '')
    
    if report_type:
        tax_reports = tax_reports.filter(report_type=report_type)
    
    if status:
        tax_reports = tax_reports.filter(status=status)
    
    if start_date:
        try:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            tax_reports = tax_reports.filter(start_date__gte=start_date_obj)
        except ValueError:
            pass
    
    if end_date:
        try:
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
            tax_reports = tax_reports.filter(end_date__lte=end_date_obj)
        except ValueError:
            pass
    
    if query:
        tax_reports = tax_reports.filter(
            Q(reference_number__icontains=query) | 
            Q(notes__icontains=query)
        )
    
    # الترتيب
    tax_reports = tax_reports.order_by('-end_date')
    
    # التصفح
    paginator = Paginator(tax_reports, 20)  # 20 تقرير في الصفحة
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'report_type': report_type,
        'status': status,
        'start_date': start_date,
        'end_date': end_date,
        'query': query,
    }
    
    return render(request, 'parts_inventory/financial/tax_reports_list.html', context)


@login_required
def generate_tax_report(request):
    """إنشاء تقرير ضريبي جديد"""
    if request.method == 'POST':
        # استخراج البيانات من النموذج
        report_type = request.POST.get('report_type')
        start_date_str = request.POST.get('start_date')
        end_date_str = request.POST.get('end_date')
        notes = request.POST.get('notes', '')
        
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            
            # حساب إجمالي ضرائب المبيعات
            total_sales_tax = SaleTax.objects.filter(
                sale__sale_date__date__gte=start_date,
                sale__sale_date__date__lte=end_date
            ).aggregate(Sum('tax_amount'))['tax_amount__sum'] or 0
            
            # حساب إجمالي ضرائب المشتريات القابلة للخصم
            total_purchase_tax = PurchaseTax.objects.filter(
                purchase__purchase_date__gte=start_date,
                purchase__purchase_date__lte=end_date,
                is_deductible=True
            ).aggregate(Sum('tax_amount'))['tax_amount__sum'] or 0
            
            # حساب الضريبة المستحقة
            tax_due = total_sales_tax - total_purchase_tax
            
            # إنشاء التقرير
            tax_report = TaxReport(
                report_type=report_type,
                start_date=start_date,
                end_date=end_date,
                status='draft',
                total_sales_tax=total_sales_tax,
                total_purchase_tax=total_purchase_tax,
                tax_due=tax_due,
                notes=notes,
                created_by=request.user
            )
            tax_report.save()
            
            messages.success(request, 'تم إنشاء التقرير الضريبي بنجاح')
            return redirect('parts_inventory:financial:tax_reports_list')
            
        except ValueError as e:
            messages.error(request, f'خطأ في البيانات المدخلة: {str(e)}')
    
    # عرض نموذج إنشاء التقرير
    context = {
        'report_types': TaxReport.REPORT_TYPES,
        'today': timezone.now().date(),
    }
    
    return render(request, 'parts_inventory/financial/generate_tax_report.html', context)


@login_required
def tax_report_detail(request, report_id):
    """عرض تفاصيل تقرير ضريبي"""
    tax_report = get_object_or_404(TaxReport, pk=report_id)
    
    # الحصول على ضرائب المبيعات المشمولة في التقرير
    sales_taxes = SaleTax.objects.filter(
        sale__sale_date__date__gte=tax_report.start_date,
        sale__sale_date__date__lte=tax_report.end_date
    ).order_by('-sale__sale_date')
    
    # الحصول على ضرائب المشتريات المشمولة في التقرير
    purchase_taxes = PurchaseTax.objects.filter(
        purchase__purchase_date__gte=tax_report.start_date,
        purchase__purchase_date__lte=tax_report.end_date,
        is_deductible=True
    ).order_by('-purchase__purchase_date')
    
    context = {
        'tax_report': tax_report,
        'sales_taxes': sales_taxes,
        'purchase_taxes': purchase_taxes,
    }
    
    return render(request, 'parts_inventory/financial/tax_report_detail.html', context)


@login_required
def update_tax_report_status(request, report_id):
    """تحديث حالة التقرير الضريبي"""
    tax_report = get_object_or_404(TaxReport, pk=report_id)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        reference_number = request.POST.get('reference_number', '')
        notes = request.POST.get('notes', '')
        
        if new_status in [status[0] for status in TaxReport.REPORT_STATUS]:
            tax_report.status = new_status
            tax_report.reference_number = reference_number
            tax_report.notes = notes
            
            # إذا تم تقديم التقرير، نسجل تاريخ التقديم
            if new_status == 'submitted' and not tax_report.submission_date:
                tax_report.submission_date = timezone.now().date()
            
            tax_report.save()
            messages.success(request, 'تم تحديث حالة التقرير بنجاح')
        else:
            messages.error(request, 'حالة التقرير غير صالحة')
        
        return redirect('parts_inventory:financial:tax_report_detail', report_id=report_id)
    
    context = {
        'tax_report': tax_report,
        'statuses': TaxReport.REPORT_STATUS,
    }
    
    return render(request, 'parts_inventory/financial/update_tax_report_status.html', context)


@login_required
def add_tax_rate(request):
    """إضافة معدل ضريبة جديد"""
    if request.method == 'POST':
        # استخراج البيانات من النموذج
        name = request.POST.get('name')
        rate = request.POST.get('rate')
        description = request.POST.get('description', '')
        is_default = 'is_default' in request.POST
        is_active = 'is_active' in request.POST
        
        try:
            # التحقق من البيانات
            rate = Decimal(rate)
            
            # إنشاء معدل الضريبة
            tax_rate = TaxRate(
                name=name,
                rate=rate,
                description=description,
                is_default=is_default,
                is_active=is_active
            )
            
            tax_rate.save()
            messages.success(request, 'تم إضافة معدل الضريبة بنجاح')
            
        except ValueError:
            messages.error(request, 'قيمة معدل الضريبة غير صالحة')
        except Exception as e:
            messages.error(request, f'حدث خطأ أثناء إضافة معدل الضريبة: {str(e)}')
    
    return redirect('parts_inventory:financial:tax_rates_list')


@login_required
def edit_tax_rate(request, tax_rate_id):
    """تعديل معدل ضريبة"""
    tax_rate = get_object_or_404(TaxRate, pk=tax_rate_id)
    
    if request.method == 'POST':
        # استخراج البيانات من النموذج
        name = request.POST.get('name')
        rate = request.POST.get('rate')
        description = request.POST.get('description', '')
        is_default = 'is_default' in request.POST
        is_active = 'is_active' in request.POST
        
        try:
            # التحقق من البيانات
            rate = Decimal(rate)
            
            # تحديث معدل الضريبة
            tax_rate.name = name
            tax_rate.rate = rate
            tax_rate.description = description
            tax_rate.is_default = is_default
            tax_rate.is_active = is_active
            
            tax_rate.save()
            messages.success(request, 'تم تحديث معدل الضريبة بنجاح')
            
        except ValueError:
            messages.error(request, 'قيمة معدل الضريبة غير صالحة')
        except Exception as e:
            messages.error(request, f'حدث خطأ أثناء تحديث معدل الضريبة: {str(e)}')
    
    return redirect('parts_inventory:financial:tax_rates_list')


@login_required
def delete_tax_rate(request, tax_rate_id):
    """حذف معدل ضريبة"""
    tax_rate = get_object_or_404(TaxRate, pk=tax_rate_id)
    
    # لا يمكن حذف معدل الضريبة الافتراضي
    if tax_rate.is_default:
        messages.error(request, 'لا يمكن حذف معدل الضريبة الافتراضي')
        return redirect('parts_inventory:financial:tax_rates_list')
    
    # التحقق من عدم استخدام معدل الضريبة في ضرائب المبيعات أو المشتريات
    sales_taxes_count = SaleTax.objects.filter(tax_rate=tax_rate).count()
    purchase_taxes_count = PurchaseTax.objects.filter(tax_rate=tax_rate).count()
    
    if sales_taxes_count > 0 or purchase_taxes_count > 0:
        messages.error(request, 'لا يمكن حذف معدل الضريبة لأنه مستخدم في ضرائب المبيعات أو المشتريات')
        return redirect('parts_inventory:financial:tax_rates_list')
    
    if request.method == 'POST':
        try:
            tax_rate.delete()
            messages.success(request, 'تم حذف معدل الضريبة بنجاح')
        except Exception as e:
            messages.error(request, f'حدث خطأ أثناء حذف معدل الضريبة: {str(e)}')
    
    return redirect('parts_inventory:financial:tax_rates_list')


@login_required
def add_purchase_tax(request):
    """إضافة ضريبة مشتريات جديدة"""
    if request.method == 'POST':
        # استخراج البيانات من النموذج
        purchase_id = request.POST.get('purchase')
        tax_rate_id = request.POST.get('tax_rate')
        tax_amount = request.POST.get('tax_amount')
        is_deductible = 'is_deductible' in request.POST
        is_claimed = 'is_claimed' in request.POST
        claim_date = request.POST.get('claim_date') or None
        reference_number = request.POST.get('reference_number') or None
        notes = request.POST.get('notes') or None
        
        try:
            # التحقق من البيانات
            purchase = Purchase.objects.get(pk=purchase_id)
            tax_rate = TaxRate.objects.get(pk=tax_rate_id)
            tax_amount = Decimal(tax_amount)
            
            # إنشاء ضريبة المشتريات
            purchase_tax = PurchaseTax(
                purchase=purchase,
                tax_rate=tax_rate,
                tax_amount=tax_amount,
                is_deductible=is_deductible,
                is_claimed=is_claimed,
                reference_number=reference_number,
                notes=notes,
                created_by=request.user
            )
            
            # إذا تم تحديد أن الضريبة تم المطالبة بها، نضيف تاريخ المطالبة
            if is_claimed and claim_date:
                try:
                    purchase_tax.claim_date = datetime.strptime(claim_date, '%Y-%m-%d').date()
                except ValueError:
                    purchase_tax.claim_date = timezone.now().date()
            
            purchase_tax.save()
            messages.success(request, 'تم إضافة ضريبة المشتريات بنجاح')
            
        except Purchase.DoesNotExist:
            messages.error(request, 'عملية الشراء غير موجودة')
        except TaxRate.DoesNotExist:
            messages.error(request, 'معدل الضريبة غير موجود')
        except ValueError:
            messages.error(request, 'قيمة مبلغ الضريبة غير صالحة')
        except Exception as e:
            messages.error(request, f'حدث خطأ أثناء إضافة ضريبة المشتريات: {str(e)}')
    
    return redirect('parts_inventory:financial:purchase_taxes_list')