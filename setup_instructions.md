# تعليمات إعداد وتشغيل نظام إدارة قطع غيار السيارات

هذا الدليل يوضح خطوات إعداد وتشغيل نظام إدارة قطع غيار السيارات على جهازك المحلي.

## متطلبات النظام

- Python 3.10 أو أحدث
- PostgreSQL 13 أو أحدث (اختياري، يمكن استخدام SQLite كبديل)
- Git (اختياري، للتحكم في الإصدارات)

## خطوات الإعداد

### 1. إعداد البيئة الافتراضية

يُفضل استخدام بيئة افتراضية لعزل متطلبات المشروع عن باقي النظام. إذا كانت البيئة الافتراضية غير موجودة، قم بإنشائها باستخدام الأوامر التالية:

```bash
# إنشاء بيئة افتراضية جديدة
python -m venv venv

# تفعيل البيئة الافتراضية
# في نظام Windows
venv\Scripts\activate

# في نظام Linux/Mac
# source venv/bin/activate
```

### 2. تثبيت المتطلبات

بعد تفعيل البيئة الافتراضية، قم بتثبيت جميع المتطلبات باستخدام الأمر التالي:

```bash
pip install -r requirements.txt
```

### 3. إعداد قاعدة البيانات

#### استخدام SQLite (الإعداد الافتراضي)

النظام مُعد افتراضيًا لاستخدام SQLite، وهي قاعدة بيانات لا تتطلب إعدادًا إضافيًا. إذا كنت تريد استخدام SQLite، يمكنك تخطي هذه الخطوة والانتقال مباشرة إلى الخطوة 4.

#### استخدام PostgreSQL (اختياري)

إذا كنت ترغب في استخدام PostgreSQL، اتبع الخطوات التالية:

1. قم بتثبيت PostgreSQL على جهازك إذا لم يكن مثبتًا بالفعل.
2. قم بإنشاء قاعدة بيانات جديدة:

```sql
CREATE DATABASE auto_parts_db;
CREATE USER auto_parts_user WITH PASSWORD 'auto_parts_user';
ALTER ROLE auto_parts_user SET client_encoding TO 'utf8';
ALTER ROLE auto_parts_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE auto_parts_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE auto_parts_db TO auto_parts_user;
```

3. قم بتعديل ملف `auto_parts_system/settings.py` لاستخدام PostgreSQL بدلاً من SQLite:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'auto_parts_db',
        'USER': 'auto_parts_user',
        'PASSWORD': 'auto_parts_user',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### 4. تطبيق الترحيلات (Migrations)

قم بتطبيق الترحيلات لإنشاء هيكل قاعدة البيانات:

```bash
python manage.py migrate
```

### 5. إنشاء مستخدم مسؤول

قم بإنشاء مستخدم مسؤول للدخول إلى لوحة الإدارة:

```bash
python manage.py createsuperuser
```

اتبع التعليمات لإدخال اسم المستخدم والبريد الإلكتروني وكلمة المرور.

### 6. جمع الملفات الثابتة (Static Files)

قم بجمع الملفات الثابتة في مجلد واحد:

```bash
python manage.py collectstatic
```

## نظام تسجيل الدخول والمصادقة

يستخدم النظام نظام المصادقة المدمج في Django للتحكم في الوصول إلى الصفحات. جميع صفحات النظام تتطلب تسجيل الدخول باستثناء صفحة تسجيل الدخول نفسها.

### إدارة المستخدمين

1. **إنشاء مستخدمين جدد**: يمكن للمسؤول إنشاء مستخدمين جدد من خلال لوحة الإدارة:
   - انتقل إلى `http://localhost:8080/admin/`
   - سجل الدخول باستخدام حساب المسؤول
   - انتقل إلى قسم "المستخدمون" وانقر على "إضافة مستخدم"
   - أدخل اسم المستخدم وكلمة المرور والبيانات المطلوبة
   - حدد الصلاحيات المناسبة للمستخدم

2. **تغيير كلمة المرور**: يمكن للمستخدمين تغيير كلمة المرور الخاصة بهم من خلال:
   - النقر على اسم المستخدم في القائمة العلوية
   - اختيار "تغيير كلمة المرور"
   - إدخال كلمة المرور الحالية وكلمة المرور الجديدة

3. **إعادة تعيين كلمة المرور**: في حالة نسيان كلمة المرور، يمكن للمستخدم طلب إعادة تعيينها من صفحة تسجيل الدخول.

### إعدادات البريد الإلكتروني (لإعادة تعيين كلمة المرور)

لتفعيل ميزة إعادة تعيين كلمة المرور عبر البريد الإلكتروني، يجب إضافة إعدادات البريد الإلكتروني في ملف `settings.py`:

```python
# إعدادات البريد الإلكتروني
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'  # استبدل بخادم SMTP الخاص بك
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@example.com'  # استبدل ببريدك الإلكتروني
EMAIL_HOST_PASSWORD = 'your-email-password'  # استبدل بكلمة مرور البريد أو رمز التطبيق
DEFAULT_FROM_EMAIL = 'Auto Parts System <your-email@example.com>'
```

### تخصيص نظام المصادقة

يمكن تخصيص نظام المصادقة من خلال تعديل القوالب الموجودة في مجلد `templates/registration/`:

- `login.html`: صفحة تسجيل الدخول
- `logged_out.html`: صفحة تأكيد تسجيل الخروج
- `password_change_form.html`: نموذج تغيير كلمة المرور
- `password_change_done.html`: تأكيد تغيير كلمة المرور
- `password_reset_form.html`: نموذج إعادة تعيين كلمة المرور
- `password_reset_done.html`: تأكيد إرسال بريد إعادة التعيين
- `password_reset_email.html`: قالب البريد الإلكتروني لإعادة التعيين
- `password_reset_confirm.html`: صفحة إعادة تعيين كلمة المرور
- `password_reset_complete.html`: تأكيد إعادة تعيين كلمة المرور

## تشغيل النظام

### تشغيل خادم التطوير

لتشغيل خادم التطوير على منفذ مختلف (مثلاً 8080)، استخدم الأمر التالي:

```bash
python manage.py runserver 8080
```

يمكنك الآن الوصول إلى النظام من خلال المتصفح على العنوان: `http://localhost:8080/`

للوصول إلى لوحة الإدارة، انتقل إلى: `http://localhost:8080/admin/`

## إعداد بيانات تجريبية (اختياري)

إذا كنت ترغب في إضافة بيانات تجريبية للنظام، يمكنك استخدام الأمر التالي:

```bash
python manage.py loaddata sample_data.json
```

ملاحظة: يجب أن يكون ملف `sample_data.json` موجودًا في مجلد `fixtures` داخل التطبيق.

## استكشاف الأخطاء وإصلاحها

### مشكلة في تثبيت المتطلبات

إذا واجهت مشاكل في تثبيت بعض الحزم، حاول تثبيتها بشكل منفصل. يمكنك تثبيت الحزم الأساسية أولاً ثم تثبيت باقي الحزم:

```bash
# تثبيت Django أولاً
pip install Django==5.0.6

# تثبيت الحزم الأساسية المطلوبة في INSTALLED_APPS
pip install django-crispy-forms==2.0
pip install crispy-bootstrap5==0.7
pip install django-filter==23.5
pip install django-tables2==2.6.0
pip install django-import-export==3.3.3
pip install django-widget-tweaks==1.5.0
pip install django-bootstrap-v5==1.0.11
pip install django-bootstrap-datepicker-plus==5.0.4
pip install django-allauth==0.58.2
pip install django-debug-toolbar==4.2.0
pip install django-extensions==3.2.3
pip install django-compressor==4.4
pip install django-cors-headers==4.3.1
pip install djangorestframework==3.14.0

# تثبيت باقي الحزم
pip install psycopg2-binary==2.9.9
pip install Pillow==10.2.0
pip install openpyxl==3.1.2
pip install xlwt==1.3.0
pip install reportlab==4.0.7
pip install weasyprint==60.2
```

#### ملاحظة هامة حول حزمة django-rest-framework

إذا واجهت خطأ عند تثبيت حزمة `django-rest-framework`، فهذا لأن الاسم الصحيح للحزمة هو `djangorestframework`. قم بتثبيتها باستخدام الأمر التالي:

```bash
pip install djangorestframework==3.14.0
```

### مشكلة في تثبيت Pillow على نظام Windows

قد تواجه مشاكل في تثبيت حزمة Pillow على نظام Windows بسبب متطلبات البناء. إليك بعض الحلول:

1. تثبيت الإصدار المناسب من Visual C++ Build Tools:
   - قم بتنزيل وتثبيت [Visual C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
   - أثناء التثبيت، تأكد من اختيار "C++ build tools" في قائمة المكونات

2. تثبيت Pillow باستخدام الحزم الثنائية المجمعة مسبقًا (wheel):

```bash
pip install --only-binary=Pillow Pillow==10.2.0
```

3. تثبيت إصدار أقدم من Pillow إذا استمرت المشكلة:

```bash
pip install Pillow==9.5.0
```

4. تثبيت المتطلبات الأخرى أولاً ثم تثبيت Pillow لاحقًا:

```bash
# قم بإنشاء نسخة من ملف المتطلبات بدون Pillow
pip install -r requirements.txt --skip-failed-builds
# ثم قم بتثبيت Pillow بشكل منفصل
pip install --only-binary=Pillow Pillow==10.2.0
```

### مشكلة في الاتصال بقاعدة البيانات

تأكد من أن خدمة PostgreSQL تعمل وأن المستخدم لديه الصلاحيات المناسبة للوصول إلى قاعدة البيانات.

### مشكلة في تشغيل الخادم على منفذ معين

إذا كان المنفذ المحدد مستخدمًا بالفعل، جرب منفذًا آخر:

```bash
python manage.py runserver 8088
```

## الإنتاج (Production)

لنشر النظام في بيئة الإنتاج، يُنصح باستخدام خادم WSGI مثل Gunicorn مع Nginx:

1. قم بتثبيت Gunicorn:

```bash
pip install gunicorn
```

2. قم بتشغيل التطبيق باستخدام Gunicorn:

```bash
gunicorn auto_parts_system.wsgi:application --bind 0.0.0.0:8000
```

3. قم بإعداد Nginx كبروكسي عكسي للتطبيق.

## الدعم والمساعدة

إذا واجهت أي مشاكل أو كانت لديك استفسارات، يرجى التواصل مع فريق الدعم الفني على البريد الإلكتروني: support@autoparts.com