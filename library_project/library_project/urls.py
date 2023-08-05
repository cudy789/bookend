"""library_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

# from website.views import home
from library.views import catalog, UserTableClass, home, new_book, new_book_isbn, new_book_manual, check_in, check_out, new_user, user_books, generate_report, import_csv
from api.views import post_new_book

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name="home"),
    path('newuser', new_user, name="newUser"),
    path('library/new', new_book, name="newBook"),
    path('library/new/manual', new_book_manual, name="newBookManual"),
    path('library/new/isbn', new_book_isbn, name="newBookISBN"),
    path('library/check-in', check_in, name="checkIn"),
    path('library/check-out', check_out, name="checkOut"),
    path('library/catalog', catalog, name="catalog"),
    path('users', UserTableClass.as_view(), name="users"),
    path('library/user-books', user_books, name="userBooks"),
    path('library/generate-report', generate_report, name="generateReport"),
    path('library/import-csv', import_csv, name="importCSV"),
    path('api/book/<str:isbn>', post_new_book, name="postnewbook"),
]
