from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.postgres.fields import ArrayField

from django.forms import ModelForm, DateInput, TimeInput, TextInput, IntegerField
from django.core.exceptions import ValidationError

# Create your models here.

class Book(models.Model):
    title = models.CharField(max_length=100)
    tags = models.JSONField(default=list, blank=True, null=True)
    authors = models.JSONField(default=list, blank=True, null=True)
    isbn = models.CharField(max_length=13, blank=True, null=True)
    isbn_image = models.ImageField(blank=True, null=True, upload_to='book_isbn_images/')
    quantity = models.IntegerField(default=0,
                                   verbose_name="Copies",
                                   validators=[
                                       MinValueValidator(0)
                                   ],
                                   blank=True, null=True)
    checkedOut = models.IntegerField(default=0,
                                     verbose_name="Checked Out",
                                     validators=[
                                         MinValueValidator(0)
                                     ],
                                     blank=True, null=True)
    subtitle = models.CharField(max_length=300, blank=True, null=True)
    publisher = models.CharField(max_length=100, blank=True, null=True)
    publishedDate = models.CharField(max_length=20, blank=True, null=True)
    description = models.CharField(max_length=5000, blank=True, null=True)
    pageCount = models.IntegerField(default=0,
                                    validators=[
                                        MinValueValidator(0)
                                    ], blank=True, null=True)
    # categories = models.JSONField(blank=True, null=True)
    averageRating = models.DecimalField(default=0,
                                        decimal_places=1,
                                        max_digits=2,
                                        validators=[
                                            MinValueValidator(0),
                                            MaxValueValidator(5)
                                        ],
                                        blank=True, null=True)
    maturityRating = models.CharField(max_length=100, blank=True, null=True)
    thumbnail = models.CharField(max_length=200, blank=True, null=True)
    publicDomain = models.BooleanField(blank=True, null=True)


class User(models.Model):
    name = models.CharField(max_length=100)
    isbns = models.JSONField(default=list, blank=True, null=True)
    card_id = models.CharField(max_length=50, verbose_name="Library Card Number")
    card_id_image = models.ImageField(blank=True, null=True, upload_to='card_id_images/')
