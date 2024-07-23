from django.contrib import admin

# Register your models here.

from .models import Book, User

# Register your models here to have them show up on the /admin page
admin.site.register(Book)
admin.site.register(User)