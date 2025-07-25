# Generated by Django 5.2.1 on 2025-05-30 00:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0021_factura_fecha_vencimiento'),
    ]

    operations = [
        migrations.AddField(
            model_name='producto',
            name='porcentaje_ganancia',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=5, verbose_name='Porcentaje de ganancia'),
        ),
        migrations.AddField(
            model_name='producto',
            name='precio_venta',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True, verbose_name='Precio de venta'),
        ),
    ]
