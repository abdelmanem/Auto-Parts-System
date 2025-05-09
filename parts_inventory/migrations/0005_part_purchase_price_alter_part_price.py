# Generated by Django 4.2.20 on 2025-03-24 20:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parts_inventory', '0004_alter_part_compatible_cars'),
    ]

    operations = [
        migrations.AddField(
            model_name='part',
            name='purchase_price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='سعر الشراء'),
        ),
        migrations.AlterField(
            model_name='part',
            name='price',
            field=models.DecimalField(decimal_places=2, max_digits=10, verbose_name='سعر البيع'),
        ),
    ]
