# Generated by Django 4.2.4 on 2024-06-02 21:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookend', '0009_alter_book_authors'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='card_id_image',
            field=models.ImageField(blank=True, null=True, upload_to='card_id_images/'),
        ),
    ]