# Generated by Django 2.1.11 on 2019-08-25 07:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('donor', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='donor',
            name='total_reimbursements_value',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=20),
        ),
    ]
