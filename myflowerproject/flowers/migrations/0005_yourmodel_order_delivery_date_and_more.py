# Generated by Django 5.1.2 on 2024-10-25 20:29

import datetime
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('flowers', '0004_rename_categories_flower_category_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='YourModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.AddField(
            model_name='order',
            name='delivery_date',
            field=models.DateField(default=datetime.date.today),
        ),
        migrations.AlterField(
            model_name='order',
            name='delivery_time',
            field=models.CharField(max_length=20),
        ),
        migrations.AlterField(
            model_name='order',
            name='order_number',
            field=models.CharField(default='N/A', max_length=50),
        ),
        migrations.AlterField(
            model_name='order',
            name='phone',
            field=models.CharField(max_length=15),
        ),
        migrations.AlterField(
            model_name='order',
            name='recipient_name',
            field=models.CharField(max_length=100),
        ),
    ]
