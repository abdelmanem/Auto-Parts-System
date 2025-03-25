// وظائف حساب وإدارة ضرائب المبيعات

document.addEventListener('DOMContentLoaded', function() {
    // عناصر النموذج
    const saleSelect = document.querySelector('select[name="sale"]');
    const taxRateSelect = document.querySelector('select[name="tax_rate"]');
    const taxAmountInput = document.querySelector('input[name="tax_amount"]');
    const isPaidCheckbox = document.getElementById('isPaid');
    const paymentDateRow = document.getElementById('paymentDateRow');
    const paymentDateInput = document.querySelector('input[name="payment_date"]');
    const referenceNumberInput = document.querySelector('input[name="reference_number"]');

    // حساب مبلغ الضريبة تلقائياً
    function calculateTaxAmount() {
        const selectedSale = saleSelect.options[saleSelect.selectedIndex];
        const selectedTaxRate = taxRateSelect.options[taxRateSelect.selectedIndex];
        
        if (selectedSale && selectedTaxRate && selectedSale.value && selectedTaxRate.value) {
            const saleAmount = parseFloat(selectedSale.textContent.split('-')[2]);
            const taxRate = parseFloat(selectedTaxRate.textContent.match(/(\d+(\.\d+)?)%/)[1]);
            
            if (!isNaN(saleAmount) && !isNaN(taxRate)) {
                const calculatedTaxAmount = (saleAmount * taxRate / 100).toFixed(2);
                taxAmountInput.value = calculatedTaxAmount;
            }
        }
    }

    // إظهار/إخفاء حقول الدفع
    function togglePaymentFields() {
        if (isPaidCheckbox.checked) {
            paymentDateRow.style.display = 'flex';
            paymentDateInput.required = true;
            // تعيين تاريخ اليوم كقيمة افتراضية
            const today = new Date().toISOString().split('T')[0];
            paymentDateInput.value = today;
        } else {
            paymentDateRow.style.display = 'none';
            paymentDateInput.required = false;
            paymentDateInput.value = '';
            referenceNumberInput.value = '';
        }
    }

    // التحقق من صحة المدخلات
    function validateForm(event) {
        const form = event.target;
        if (!form.checkValidity()) {
            event.preventDefault();
            event.stopPropagation();
            
            // عرض رسائل الخطأ
            Array.from(form.elements).forEach(element => {
                if (!element.validity.valid) {
                    element.classList.add('is-invalid');
                }
            });

            // إظهار تنبيه للمستخدم
            alert('يرجى ملء جميع الحقول المطلوبة بشكل صحيح');
        }
        form.classList.add('was-validated');
    }

    // إضافة مستمعي الأحداث
    saleSelect.addEventListener('change', calculateTaxAmount);
    taxRateSelect.addEventListener('change', calculateTaxAmount);
    isPaidCheckbox.addEventListener('change', togglePaymentFields);
    
    // إضافة مستمع التحقق من صحة النموذج
    const form = document.querySelector('form[action*="add_sales_tax"]');
    if (form) {
        form.addEventListener('submit', validateForm);
    }

    // تطبيق الحالة الأولية
    togglePaymentFields();
}));