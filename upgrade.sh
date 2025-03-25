#!/bin/bash

# تعليمات ترقية نظام إدارة قطع غيار السيارات على خوادم Linux

# التأكد من تفعيل البيئة الافتراضية
if [ ! -f "venv/bin/activate" ]; then
    echo "لم يتم العثور على البيئة الافتراضية. يرجى تشغيل install.sh أولاً."
    exit 1
fi

# تفعيل البيئة الافتراضية
source venv/bin/activate

# تحديث pip
echo "جاري تحديث pip..."
pip install --upgrade pip

# تحديث المتطلبات
echo "جاري تحديث المتطلبات..."
pip install -r requirements.txt --upgrade

# تطبيق الترحيلات الجديدة
echo "جاري تطبيق الترحيلات الجديدة..."
python manage.py migrate

# تحديث الملفات الثابتة
echo "جاري تحديث الملفات الثابتة..."
python manage.py collectstatic --noinput

echo "تم اكتمال عملية الترقية بنجاح!"