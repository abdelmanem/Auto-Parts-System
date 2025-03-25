#!/bin/bash

# تعليمات تثبيت نظام إدارة قطع غيار السيارات على خوادم Linux

# التأكد من وجود Python
if ! command -v python3 &> /dev/null; then
    echo "Python 3 غير مثبت. جاري التثبيت..."
    sudo apt-get update
    sudo apt-get install -y python3 python3-pip python3-venv
fi

# إنشاء وتفعيل البيئة الافتراضية
if [ ! -d "venv" ]; then
    echo "جاري إنشاء البيئة الافتراضية..."
    python3 -m venv venv
fi

# تفعيل البيئة الافتراضية
source venv/bin/activate

# تثبيت المتطلبات
echo "جاري تثبيت المتطلبات..."
pip install --upgrade pip
pip install -r requirements.txt

# تطبيق الترحيلات
echo "جاري تطبيق الترحيلات..."
python manage.py migrate

# جمع الملفات الثابتة
echo "جاري جمع الملفات الثابتة..."
python manage.py collectstatic --noinput

# إنشاء المستخدم المشرف
echo "هل تريد إنشاء مستخدم مشرف؟ (نعم/لا)"
read create_superuser
if [ "$create_superuser" = "نعم" ]; then
    python manage.py createsuperuser
fi

echo "تم اكتمال عملية التثبيت بنجاح!"