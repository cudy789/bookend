# Generated by Django 4.2.4 on 2024-06-23 00:44

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookend', '0012_alter_book_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='isbn',
            field=models.CharField(default=0, max_length=13),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='book',
            name='quantity',
            field=models.IntegerField(blank=True, default=1, null=True, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Copies'),
        ),
    ]
