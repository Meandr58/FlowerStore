# Generated by Django 5.1.2 on 2024-12-09 22:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('flowers', '0014_orderitem'),
    ]

    operations = [
        migrations.AlterField(
            model_name='flowerimage',
            name='image',
            field=models.ImageField(upload_to='flower_images/'),
        ),
    ]
