# Generated by Django 4.2.4 on 2024-06-09 06:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookend', '0011_remove_book_categories'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='description',
            field=models.CharField(blank=True, max_length=5000, null=True),
        ),
    ]
