# Generated by Django 4.2.14 on 2024-07-23 15:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mesa', '0009_settings_customer_details'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='settings',
            name='domain_controller',
        ),
        migrations.RemoveField(
            model_name='settings',
            name='domain_fqdn',
        ),
        migrations.RemoveField(
            model_name='settings',
            name='domain_password',
        ),
        migrations.RemoveField(
            model_name='settings',
            name='domain_user',
        ),
        migrations.RemoveField(
            model_name='settings',
            name='neo4j_password',
        ),
        migrations.RemoveField(
            model_name='settings',
            name='neo4j_user',
        ),
    ]
