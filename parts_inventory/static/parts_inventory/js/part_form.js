$(document).ready(function() {
    // تفعيل Select2 للقوائم المنسدلة مع خاصية البحث
    $('.select2-search').select2({
        theme: 'bootstrap-5',
        language: 'ar',
        dir: 'rtl',
        width: '100%',
        placeholder: 'اختر...',
        allowClear: true
    });

    // تفعيل Select2 للقوائم المنسدلة متعددة الاختيارات
    $('#car_models').select2({
        theme: 'bootstrap-5',
        language: 'ar',
        dir: 'rtl',
        width: '100%',
        placeholder: 'اختر موديلات السيارات',
        allowClear: true
    });
});