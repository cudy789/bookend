# Generated by Django 4.2.4 on 2024-06-02 20:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookend', '0008_alter_book_isbn_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='authors',
            field=models.JSONField(blank=True, default=list, null=True),
        ),
    ]
