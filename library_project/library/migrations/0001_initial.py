# Generated by Django 4.1.5 on 2023-01-29 13:45

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Book',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('subtitle', models.CharField(max_length=300)),
                ('authors', models.JSONField()),
                ('publisher', models.CharField(max_length=100)),
                ('publishedDate', models.CharField(max_length=20)),
                ('description', models.CharField(max_length=500)),
                ('isbn', models.CharField(max_length=13)),
                ('pageCount', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)])),
                ('categories', models.JSONField()),
                ('averageRating', models.DecimalField(decimal_places=1, default=0, max_digits=2, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(5)])),
                ('maturityRating', models.CharField(max_length=100)),
                ('thumbnail', models.CharField(max_length=200)),
                ('publicDomain', models.BooleanField()),
                ('quantity', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Copies')),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('isbns', models.JSONField(default=list)),
                ('card_id', models.CharField(max_length=50)),
            ],
        ),
    ]
