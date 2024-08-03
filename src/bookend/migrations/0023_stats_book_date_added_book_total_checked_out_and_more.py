# Generated by Django 4.2.4 on 2024-08-03 20:17

import datetime
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookend', '0022_alter_book_isbn_image_alter_book_thumbnail_image_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Stats',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_books', models.IntegerField(default=0)),
                ('total_checked_out', models.IntegerField(default=0)),
                ('total_users', models.IntegerField(default=0)),
                ('users_with_most_books', models.JSONField(blank=True, default=list, null=True)),
                ('most_checked_out_books', models.JSONField(blank=True, default=list, null=True)),
                ('most_recent_checked_out', models.JSONField(blank=True, default=list, null=True)),
                ('newest_books', models.JSONField(blank=True, default=list, null=True)),
                ('newest_users', models.JSONField(blank=True, default=list, null=True)),
                ('books_with_most_copies', models.JSONField(blank=True, default=list, null=True)),
            ],
        ),
        migrations.AddField(
            model_name='book',
            name='date_added',
            field=models.DateTimeField(blank=True, default=datetime.datetime.now),
        ),
        migrations.AddField(
            model_name='book',
            name='total_checked_out',
            field=models.IntegerField(blank=True, default=0, null=True, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Total Checked Out'),
        ),
        migrations.AddField(
            model_name='user',
            name='date_added',
            field=models.DateTimeField(blank=True, default=datetime.datetime.now),
        ),
        migrations.AddField(
            model_name='user',
            name='lifetime_chcked_out',
            field=models.IntegerField(default=0),
        ),
    ]
