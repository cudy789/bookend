# Generated by Django 4.2.4 on 2024-06-02 19:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookend', '0007_alter_book_isbn_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='isbn_image',
            field=models.ImageField(blank=True, null=True, upload_to='book_isbn_images/'),
        ),
    ]
