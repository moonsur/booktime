# Generated by Django 4.0.4 on 2022-06-05 06:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_basket_basketline'),
    ]

    operations = [
        migrations.AlterField(
            model_name='address',
            name='address1',
            field=models.CharField(max_length=120, verbose_name='Address Line 1'),
        ),
        migrations.AlterField(
            model_name='address',
            name='address2',
            field=models.CharField(max_length=120, verbose_name='Address Line 2'),
        ),
        migrations.AlterField(
            model_name='address',
            name='name',
            field=models.CharField(max_length=60),
        ),
    ]
