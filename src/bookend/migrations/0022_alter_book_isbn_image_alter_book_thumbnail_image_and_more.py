# Generated by Django 4.2.4 on 2024-07-31 03:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookend', '0021_alter_book_isbn_image_alter_book_thumbnail_image_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='isbn_image',
            field=models.ImageField(blank=True, null=True, upload_to='website/static/data/book_isbn_images/'),
        ),
        migrations.AlterField(
            model_name='book',
            name='thumbnail_image',
            field=models.ImageField(blank=True, null=True, upload_to='website/static/data/book_cover_images/'),
        ),
        migrations.AlterField(
            model_name='user',
            name='card_id_image',
            field=models.ImageField(blank=True, null=True, upload_to='website/static/data/card_id_images/'),
        ),
    ]
