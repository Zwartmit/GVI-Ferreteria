# Generated by Django 5.2.1 on 2025-05-26 16:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0012_remove_proveedor_email_remove_proveedor_telefono'),
    ]

    operations = [
        migrations.AddField(
            model_name='factura',
            name='cancelada_manual',
            field=models.BooleanField(default=False, verbose_name='Cancelada manualmente'),
        ),
    ]
