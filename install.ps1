# تعليمات تثبيت نظام إدارة قطع غيار السيارات على خوادم Windows

# التأكد من وجود Python
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "Python غير مثبت. يرجى تثبيت Python 3.10 أو أحدث من الموقع الرسمي:"
    Write-Host "https://www.python.org/downloads/"
    exit 1
}

# التأكد من وجود pip
if (-not (Get-Command pip -ErrorAction SilentlyContinue)) {
    Write-Host "pip غير مثبت. جاري التثبيت..."
    python -m ensurepip --default-pip
}

# إنشاء وتفعيل البيئة الافتراضية
if (-not (Test-Path "venv")) {
    Write-Host "جاري إنشاء البيئة الافتراضية..."
    python -m venv venv
}

# تفعيل البيئة الافتراضية
.\venv\Scripts\Activate.ps1

# تثبيت المتطلبات
Write-Host "جاري تثبيت المتطلبات..."
python -m pip install --upgrade pip
pip install -r requirements.txt

# تطبيق الترحيلات
Write-Host "جاري تطبيق الترحيلات..."
python manage.py migrate

# جمع الملفات الثابتة
Write-Host "جاري جمع الملفات الثابتة..."
python manage.py collectstatic --noinput

# إنشاء المستخدم المشرف
$create_superuser = Read-Host "هل تريد إنشاء مستخدم مشرف؟ (نعم/لا)"
if ($create_superuser -eq "نعم") {
    python manage.py createsuperuser
}

Write-Host "تم اكتمال عملية التثبيت بنجاح!"