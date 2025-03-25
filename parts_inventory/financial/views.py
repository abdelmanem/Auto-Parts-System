from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, Q, F
from django.utils import timezone
from django.core.paginator import Paginator
from datetime import datetime, timedelta
from .models import (
    FinancialAccount, Transaction, Debt,
    DebtPayment, ProfitLossReport
)
from parts_inventory.models import Sale, Purchase, SaleItem, PurchaseItem
from .inventory_movement import InventoryMovement


@login_required
def financial_dashboard(request):
    """عرض لوحة التحكم المالية الرئيسية"""
    # إحصائيات عامة
    total_receivable = Debt.objects.filter(debt_type='receivable', is_paid=False).aggregate(Sum('remaining_amount'))['remaining_amount__sum'] or 0
    total_payable = Debt.objects.filter(debt_type='payable', is_paid=False).aggregate(Sum('remaining_amount'))['remaining_amount__sum'] or 0
    
    # الديون المستحقة قريباً (خلال 30 يوم)
    thirty_days_later = timezone.now().date() + timedelta(days=30)
    upcoming_receivables = Debt.objects.filter(
        debt_type='receivable',
        is_paid=False,
        due_date__lte=thirty_days_later
    ).order_by('due_date')[:5]
    
    upcoming_payables = Debt.objects.filter(
        debt_type='payable',
        is_paid=False,
        due_date__lte=thirty_days_later
    ).order_by('due_date')[:5]
    
    # آخر المعاملات المالية
    recent_transactions = Transaction.objects.all().order_by('-transaction_date')[:10]
    
    # إحصائيات الربح والخسارة للشهر الحالي
    today = timezone.now().date()
    start_of_month = today.replace(day=1)
    
    # إجمالي المبيعات للشهر الحالي
    current_month_sales = Sale.objects.filter(
        sale_date__date__gte=start_of_month,
        sale_date__date__lte=today,
        status='completed'
    ).aggregate(Sum('final_amount'))['final_amount__sum'] or 0
    
    # إجمالي المشتريات للشهر الحالي
    current_month_purchases = Purchase.objects.filter(
        purchase_date__gte=start_of_month,
        purchase_date__lte=today,
        status='received'
    ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    
    # إجمالي المصروفات للشهر الحالي (من المعاملات المالية)
    current_month_expenses = Transaction.objects.filter(
        transaction_date__gte=start_of_month,
        transaction_date__lte=today,
        transaction_type='expense'
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    # حساب صافي الربح التقريبي
    estimated_profit = current_month_sales - current_month_purchases - current_month_expenses
    
    context = {
        'total_receivable': total_receivable,
        'total_payable': total_payable,
        'upcoming_receivables': upcoming_receivables,
        'upcoming_payables': upcoming_payables,
        'recent_transactions': recent_transactions,
        'current_month_sales': current_month_sales,
        'current_month_purchases': current_month_purchases,
        'current_month_expenses': current_month_expenses,
        'estimated_profit': estimated_profit,
    }
    
    return render(request, 'parts_inventory/financial/dashboard.html', context)


@login_required
def accounts_list(request):
    """عرض قائمة الحسابات المالية"""
    accounts = FinancialAccount.objects.all()
    
    # تطبيق الفلاتر
    account_type = request.GET.get('account_type', '')
    query = request.GET.get('q', '')
    
    if account_type:
        accounts = accounts.filter(account_type=account_type)
    
    if query:
        accounts = accounts.filter(
            Q(name__icontains=query) | 
            Q(code__icontains=query) | 
            Q(description__icontains=query)
        )
    
    # الترتيب
    accounts = accounts.order_by('code')
    
    # التصفح
    paginator = Paginator(accounts, 20)  # 20 حساب في الصفحة
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'account_type': account_type,
        'query': query,
    }
    
    return render(request, 'parts_inventory/financial/accounts_list.html', context)


@login_required
def transactions_list(request):
    """عرض قائمة المعاملات المالية"""
    transactions = Transaction.objects.all()
    
    # تطبيق الفلاتر
    transaction_type = request.GET.get('transaction_type', '')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
    query = request.GET.get('q', '')
    
    if transaction_type:
        transactions = transactions.filter(transaction_type=transaction_type)
    
    if start_date:
        try:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            transactions = transactions.filter(transaction_date__gte=start_date_obj)
        except ValueError:
            pass
    
    if end_date:
        try:
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
            transactions = transactions.filter(transaction_date__lte=end_date_obj)
        except ValueError:
            pass
    
    if query:
        transactions = transactions.filter(
            Q(description__icontains=query) | 
            Q(reference_number__icontains=query) | 
            Q(debit_account__name__icontains=query) | 
            Q(credit_account__name__icontains=query)
        )
    
    # الترتيب
    transactions = transactions.order_by('-transaction_date')
    
    # التصفح
    paginator = Paginator(transactions, 20)  # 20 معاملة في الصفحة
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'transaction_type': transaction_type,
        'start_date': start_date,
        'end_date': end_date,
        'query': query,
    }
    
    return render(request, 'parts_inventory/financial/transactions_list.html', context)


@login_required
def debts_list(request):
    """عرض قائمة الديون والمديونيات"""
    debts = Debt.objects.all()
    
    # تطبيق الفلاتر
    debt_type = request.GET.get('debt_type', '')
    is_paid = request.GET.get('is_paid', '')
    due_date_filter = request.GET.get('due_date_filter', '')
    query = request.GET.get('q', '')
    
    if debt_type:
        debts = debts.filter(debt_type=debt_type)
    
    if is_paid != '':
        is_paid_bool = is_paid == 'true'
        debts = debts.filter(is_paid=is_paid_bool)
    
    if due_date_filter == 'overdue':
        debts = debts.filter(due_date__lt=timezone.now().date(), is_paid=False)
    elif due_date_filter == 'upcoming':
        thirty_days_later = timezone.now().date() + timedelta(days=30)
        debts = debts.filter(due_date__lte=thirty_days_later, due_date__gte=timezone.now().date(), is_paid=False)
    
    if query:
        debts = debts.filter(
            Q(customer_name__icontains=query) | 
            Q(supplier__name__icontains=query) | 
            Q(description__icontains=query)
        )
    
    # الترتيب
    debts = debts.order_by('due_date')
    
    # التصفح
    paginator = Paginator(debts, 20)  # 20 دين في الصفحة
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'debt_type': debt_type,
        'is_paid': is_paid,
        'due_date_filter': due_date_filter,
        'query': query,
    }
    
    return render(request, 'parts_inventory/financial/debts_list.html', context)


@login_required
def inventory_movements_list(request):
    """عرض قائمة حركات المخزون"""
    movements = InventoryMovement.objects.all()
    
    # تطبيق الفلاتر
    movement_type = request.GET.get('movement_type', '')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
    query = request.GET.get('q', '')
    
    if movement_type:
        movements = movements.filter(movement_type=movement_type)
    
    if start_date:
        try:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            movements = movements.filter(created_at__date__gte=start_date_obj)
        except ValueError:
            pass
    
    if end_date:
        try:
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
            movements = movements.filter(created_at__date__lte=end_date_obj)
        except ValueError:
            pass
    
    if query:
        movements = movements.filter(
            Q(part__name__icontains=query) | 
            Q(part__part_number__icontains=query) | 
            Q(reference_number__icontains=query) | 
            Q(notes__icontains=query)
        )
    
    # الترتيب
    movements = movements.order_by('-created_at')
    
    # التصفح
    paginator = Paginator(movements, 20)  # 20 حركة في الصفحة
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'movement_type': movement_type,
        'start_date': start_date,
        'end_date': end_date,
        'query': query,
        'movement_types': dict(InventoryMovement.MOVEMENT_TYPES)
    }
    
    return render(request, 'parts_inventory/financial/inventory_movements_list.html', context)


@login_required
def inventory_movements_list(request):
    """عرض قائمة حركات المخزون"""
    movements = InventoryMovement.objects.all()
    
    # تطبيق الفلاتر
    movement_type = request.GET.get('movement_type', '')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
    query = request.GET.get('q', '')
    
    if movement_type:
        movements = movements.filter(movement_type=movement_type)
    
    if start_date:
        try:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            movements = movements.filter(created_at__date__gte=start_date_obj)
        except ValueError:
            pass
    
    if end_date:
        try:
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
            movements = movements.filter(created_at__date__lte=end_date_obj)
        except ValueError:
            pass
    
    if query:
        movements = movements.filter(
            Q(part__name__icontains=query) | 
            Q(part__part_number__icontains=query) | 
            Q(reference_number__icontains=query) | 
            Q(notes__icontains=query)
        )
    
    # الترتيب
    movements = movements.order_by('-created_at')
    
    # التصفح
    paginator = Paginator(movements, 20)  # 20 حركة في الصفحة
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'movement_type': movement_type,
        'start_date': start_date,
        'end_date': end_date,
        'query': query,
        'movement_types': dict(InventoryMovement.MOVEMENT_TYPES)
    }
    
    return render(request, 'parts_inventory/financial/inventory_movements_list.html', context)

@login_required
def add_inventory_movement(request):
    """إضافة حركة مخزون جديدة"""
    if request.method == 'POST':
        # معالجة البيانات المرسلة
        part_id = request.POST.get('part')
        quantity = request.POST.get('quantity')
        movement_type = request.POST.get('movement_type')
        reference_number = request.POST.get('reference_number')
        notes = request.POST.get('notes')
        
        try:
            part = Part.objects.get(id=part_id)
            movement = InventoryMovement.objects.create(
                part=part,
                quantity=quantity,
                movement_type=movement_type,
                reference_number=reference_number,
                notes=notes,
                created_by=request.user
            )
            messages.success(request, 'تمت إضافة حركة المخزون بنجاح')
            return redirect('parts_inventory:financial:inventory_movements_list')
        except (Part.DoesNotExist, ValueError) as e:
            messages.error(request, 'حدث خطأ أثناء إضافة حركة المخزون')
    
    # عرض نموذج إضافة حركة مخزون جديدة
    parts = Part.objects.all()
    context = {
        'parts': parts,
        'movement_types': InventoryMovement.MOVEMENT_TYPES
    }
    return render(request, 'parts_inventory/financial/add_inventory_movement.html', context)

@login_required
def add_inventory_movement(request):
    """إضافة حركة مخزون جديدة"""
    if request.method == 'POST':
        # معالجة البيانات المرسلة
        part_id = request.POST.get('part')
        quantity = request.POST.get('quantity')
        movement_type = request.POST.get('movement_type')
        reference_number = request.POST.get('reference_number')
        notes = request.POST.get('notes')
        
        try:
            part = Part.objects.get(id=part_id)
            movement = InventoryMovement.objects.create(
                part=part,
                quantity=quantity,
                movement_type=movement_type,
                reference_number=reference_number,
                notes=notes,
                created_by=request.user
            )
            messages.success(request, 'تمت إضافة حركة المخزون بنجاح')
            return redirect('parts_inventory:financial:inventory_movements_list')
        except (Part.DoesNotExist, ValueError) as e:
            messages.error(request, 'حدث خطأ أثناء إضافة حركة المخزون')
    
    # عرض نموذج إضافة حركة مخزون جديدة
    parts = Part.objects.all()
    context = {
        'parts': parts,
        'movement_types': InventoryMovement.MOVEMENT_TYPES
    }
    return render(request, 'parts_inventory/financial/add_inventory_movement.html', context)

@login_required
def add_debt(request):
    """إضافة دين جديد"""
    if request.method == 'POST':
        # معالجة البيانات المرسلة
        debt_type = request.POST.get('debt_type')
        customer_name = request.POST.get('customer_name')
        supplier_id = request.POST.get('supplier')
        original_amount = request.POST.get('original_amount')
        remaining_amount = request.POST.get('remaining_amount')
        due_date = request.POST.get('due_date')
        reference_number = request.POST.get('reference_number')
        is_paid = request.POST.get('is_paid') == 'on'
        
        try:
            # إنشاء كائن الدين
            debt = Debt(
                debt_type=debt_type,
                customer_name=customer_name if debt_type == 'receivable' else None,
                supplier_id=supplier_id if debt_type == 'payable' else None,
                original_amount=original_amount,
                remaining_amount=remaining_amount,
                due_date=due_date,
                reference_number=reference_number,
                is_paid=is_paid,
                created_by=request.user
            )
            debt.save()
            messages.success(request, 'تمت إضافة الدين بنجاح')
        except Exception as e:
            messages.error(request, 'حدث خطأ أثناء إضافة الدين')
        
        return redirect('parts_inventory:financial:debts_list')
    
    # في حالة طلب GET، قم بإعادة توجيه المستخدم إلى قائمة الديون
    return redirect('parts_inventory:financial:debts_list')

@login_required
def profit_loss_report(request):
    """عرض تقرير الربح والخسارة"""
    # تحديد الفترة الزمنية
    today = timezone.now().date()
    start_date_str = request.GET.get('start_date', '')
    end_date_str = request.GET.get('end_date', '')
    period = request.GET.get('period', 'month')
    
    # تحديد الفترة الافتراضية (الشهر الحالي)
    if not start_date_str:
        if period == 'month':
            start_date = today.replace(day=1)  # بداية الشهر الحالي
            end_date = today
        elif period == 'quarter':
            current_quarter = (today.month - 1) // 3 + 1
            start_date = datetime(today.year, 3 * current_quarter - 2, 1).date()  # بداية الربع الحالي
            end_date = today
        elif period == 'year':
            start_date = today.replace(month=1, day=1)  # بداية السنة الحالية
            end_date = today
        else:  # custom
            start_date = today - timedelta(days=30)  # آخر 30 يوم
            end_date = today
    else:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else today
        except ValueError:
            start_date = today.replace(day=1)
            end_date = today
    
    # حساب إجمالي المبيعات
    total_sales = Sale.objects.filter(
        sale_date__date__gte=start_date,
        sale_date__date__lte=end_date,
        status='completed'
    ).aggregate(Sum('final_amount'))['final_amount__sum'] or 0
    
    # حساب تكلفة البضائع المباعة
    cost_of_goods = SaleItem.objects.filter(
        sale__sale_date__date__gte=start_date,
        sale__sale_date__date__lte=end_date,
        sale__status='completed'
    ).annotate(
        cost=F('part__purchase_items__unit_price') * F('quantity')
    ).aggregate(Sum('cost'))['cost__sum'] or 0
    
    # حساب إجمالي المصروفات
    total_expenses = Transaction.objects.filter(
        transaction_date__gte=start_date,
        transaction_date__lte=end_date,
        transaction_type='expense'
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    # حساب إجمالي الربح والصافي
    gross_profit = total_sales - cost_of_goods
    net_profit = gross_profit - total_expenses
    
    # حفظ التقرير إذا تم طلب ذلك
    if request.method == 'POST' and 'save_report' in request.POST:
        report = ProfitLossReport(
            start_date=start_date,
            end_date=end_date,
            total_sales=total_sales,
            total_cost_of_goods=cost_of_goods,
            gross_profit=gross_profit,
            total_expenses=total_expenses,
            net_profit=net_profit,
            created_by=request.user
        )
        report.save()
        messages.success(request, 'تم حفظ التقرير بنجاح')
        return redirect('parts_inventory:financial:profit_loss_report')
    
    context = {
        'start_date': start_date,
        'end_date': end_date,
        'period': period,
        'total_sales': total_sales,
        'cost_of_goods': cost_of_goods,
        'gross_profit': gross_profit,
        'total_expenses': total_expenses,
        'net_profit': net_profit,
    }
    
    return render(request, 'parts_inventory/financial/profit_loss_report.html', context)