# تعليمات ترقية نظام إدارة قطع غيار السيارات على خوادم Windows

# التأكد من وجود البيئة الافتراضية
if (-not (Test-Path "venv\Scripts\Activate.ps1")) {
    Write-Host "لم يتم العثور على البيئة الافتراضية. يرجى تشغيل install.ps1 أولاً."
    exit 1
}

# تفعيل البيئة الافتراضية
.\venv\Scripts\Activate.ps1

# تحديث pip
Write-Host "جاري تحديث pip..."
python -m pip install --upgrade pip

# تحديث المتطلبات
Write-Host "جاري تحديث المتطلبات..."
pip install -r requirements.txt --upgrade

# تطبيق الترحيلات الجديدة
Write-Host "جاري تطبيق الترحيلات الجديدة..."
python manage.py migrate

# تحديث الملفات الثابتة
Write-Host "جاري تحديث الملفات الثابتة..."
python manage.py collectstatic --noinput

Write-Host "تم اكتمال عملية الترقية بنجاح!"