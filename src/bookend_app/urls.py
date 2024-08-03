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
from bookend.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name="home"),
    path('l', kiosk, name="kiosk"),
    path('newuser', new_user, name="newUser"),
    path('removeuser', remove_user, name="removeUser"),
    path('users/<card_id>', user_details, name="userDetails"),
    # path('users/Corey', user_details, name="userDetails"),
    path('library/new', new_book, name="newBook"),
    path('library/remove', remove_book, name="removeBook"),
    path('library/new/manual', new_book_manual, name="newBookManual"),
    path('library/new/isbn', new_book_isbn, name="newBookISBN"),
    path('library/book/<isbn>', book_details, name="bookDetails"),
    # path('library/book/book_isbn_images/<str:filename>', book_isbn, name="bookISBN"),
    # path('library/book_cover_images/<str:filename>', book_cover_image, name="bookCoverImage"),
    # path('users/card_id_images/<str:filename>', user_card_image, name="userCardImage"),
    path('library/check-in', check_in, name="checkIn"),
    path('library/check-out', check_out, name="checkOut"),
    path('library/catalog', catalog, name="catalog"),
    path('users', all_users, name="users"),
    path('library/user-books', user_books, name="userBooks"),
    path('library/download-report', download_report, name="downloadReport"),
    path('library/books-report', books_report, name="booksReport"),
    path('library/users-report', users_report, name="usersReport"),
    path('library/import-csv', import_csv, name="importCSV"),
    path('library/sticker-wizard', sticker_wizard, name="stickerWizard"),
    path('settings', settings, name="settings"),
    path('stats', stats, name="stats"),
    path('settings/clean-author-fields', clean_author_fields, name="cleanAuthorFields"),
    path('settings/generate-barcodes', generate_barcodes, name="generateIsbnBarcodes"),
]


