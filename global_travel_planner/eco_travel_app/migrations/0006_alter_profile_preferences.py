# Generated by Django 5.1.1 on 2024-12-11 16:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eco_travel_app', '0005_hotel_delete_customuser_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='preferences',
            field=models.TextField(blank=True),
        ),
    ]
