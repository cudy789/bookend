from datetime import datetime

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.

class Book(models.Model):
    title = models.CharField(max_length=100)
    tags = models.JSONField(default=list, blank=True, null=True)
    authors = models.JSONField(default=list, blank=True, null=True)
    isbn = models.CharField(max_length=13)
    isbn_image = models.ImageField(blank=True, null=True, upload_to='website/static/data/book_isbn_images/')
    quantity = models.IntegerField(default=1,
                                   verbose_name="Copies",
                                   validators=[
                                       MinValueValidator(0)
                                   ],
                                   blank=True, null=True)
    checkedOut = models.IntegerField(default=0,
                                     verbose_name="Checked out",
                                     validators=[
                                         MinValueValidator(0)
                                     ],
                                     blank=True, null=True)
    total_checked_out = models.IntegerField(default=0,
                                          verbose_name="Lifetime checked out",
                                          validators=[
                                              MinValueValidator(0)
                                          ],
                                          blank=True, null=True)
    date_added = models.DateTimeField(default=datetime.now, blank=True)
    subtitle = models.CharField(max_length=300, blank=True, null=True)
    publisher = models.CharField(max_length=100, blank=True, null=True)
    publishedDate = models.CharField(max_length=20, blank=True, null=True, verbose_name="Date published")
    description = models.CharField(max_length=5000, blank=True, null=True)
    pageCount = models.IntegerField(default=0,
                                    validators=[
                                        MinValueValidator(0)
                                    ], blank=True, null=True, verbose_name="Page count")
    # categories = models.JSONField(blank=True, null=True)
    averageRating = models.DecimalField(default=0,
                                        decimal_places=1,
                                        max_digits=2,
                                        validators=[
                                            MinValueValidator(0),
                                            MaxValueValidator(5)
                                        ],
                                        blank=True, null=True, verbose_name="Average rating")
    maturityRating = models.CharField(max_length=100, blank=True, null=True, verbose_name="Maturity rating")
    thumbnail = models.CharField(max_length=200, blank=True, null=True)
    thumbnail_image = models.ImageField(blank=True, null=True, upload_to='website/static/data/book_cover_images/')
    publicDomain = models.BooleanField(blank=True, null=True, verbose_name="Public domain")


class User(models.Model):
    name = models.CharField(max_length=100)
    isbns = models.JSONField(default=list, blank=True, null=True)
    card_id = models.CharField(max_length=50, verbose_name="Library Card Number")
    card_id_image = models.ImageField(blank=True, null=True, upload_to='website/static/data/card_id_images/')
    lifetime_checked_out = models.IntegerField(default=0)
    date_added = models.DateTimeField(default=datetime.now, blank=True)
    checkout_history = models.JSONField(default=list, blank=True)

class AppMetadata(models.Model):
    app_name = models.CharField(max_length=100, default="Bookend")

class Stats(models.Model):
    total_books = models.IntegerField(default=0)
    total_checked_out = models.IntegerField(default=0)
    total_users = models.IntegerField(default=0)
    users_with_most_books = models.JSONField(default=list, blank=True, null=True)
    most_checked_out_books = models.JSONField(default=list, blank=True, null=True)
    most_recent_checked_out = models.JSONField(default=list, blank=True, null=True)
    newest_books = models.JSONField(default=list, blank=True, null=True)
    newest_users = models.JSONField(default=list, blank=True, null=True)
    books_with_most_copies = models.JSONField(default=list, blank=True, null=True)
