# Generated by Django 4.2.6 on 2023-11-16 16:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mesa', '0008_mesajob_visible'),
    ]

    operations = [
        migrations.AddField(
            model_name='settings',
            name='customer_initials',
            field=models.CharField(default='ACME', max_length=20),
        ),
        migrations.AddField(
            model_name='settings',
            name='customer_name',
            field=models.CharField(default='Acme Corporation', max_length=255),
        ),
    ]
