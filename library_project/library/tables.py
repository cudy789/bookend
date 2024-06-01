import django_tables2 as tables
from django.utils.html import format_html
from .models import Book, User

class ImageColumn(tables.Column):
    def render(self, value):
        return format_html('<img src="{}" />', value)

class AuthorColumn(tables.Column):
    def render(self, value):
        res = ''
        for author in value:
            if type(author) is list and len(author) > 0:
                author = author[0]
                print(author)
            res += str(author) + ', '

        if len(res) > 0 and res[:-2] == ", ":
            return res[:-1]
        else:
            return res

class CategoriesColumn(tables.Column):
    def render(self, value):
        print(f"value: {value}")
        res = ''
        for category in value:
            if type(category) is list and len(category) > 0:
                category = category[0]
                print(category)
            res += str(category) + ', '

        if len(res) > 0 and res[:-2] == ", ":
            return res[:-1]
        else:
            return res

class CheckedOutBooksColumn(tables.Column):
    def render(self, value):
        res = ''
        for i, isbn in enumerate(value):
            if type(isbn) is str and len(isbn) > 0:
                # Books.objects.filter(isbn=isbn)
                isbn = Book.objects.filter(isbn=isbn)[0].title
                if len(value) > 1 and i < len(value) - 1:
                    isbn += ", "
                # isbn = "its a book!"
            res += str(isbn)
        if len(res) > 0 and res[:-2] == ", ":
            return res[:-1]
        else:
            return res
class ISBNColumn(tables.Column):
    def render(self, value):
        res = ''
        for isbn in value:
            if type(isbn) is str and len(isbn) > 0:
                # isbn = author[0]
                print(isbn)
            res += str(isbn) + ', '

        if len(res) > 0 and res[:-2] == ", ":
            return res[:-1]
        else:
            return res


class BookTable(tables.Table):
    thumbnail = ImageColumn('Cover')
    authors = AuthorColumn('Authors')
    class Meta:
        model = Book
        attrs = {"class": "table",
                 'thead': {
                     'class': 'thead-dark'
                 }}
        fields = ("thumbnail", "title", "authors", "quantity", "checkedOut", "isbn")

class UserBookTable(tables.Table):
    thumbnail = ImageColumn('Cover')
    authors = AuthorColumn('Authors')
    class Meta:
        model = Book
        attrs = {"class": "table",
                 'thead': {
                     'class': 'thead-dark'
                 }}
        fields = ("thumbnail", "title", "authors", "isbn")

class UserTable(tables.Table):
    isbns = CheckedOutBooksColumn('Books')

    class Meta:
        model = User
        attrs = {"class": "table",
                 'thead': {
                     'class': 'thead-dark'
                 }}
        fields = ("name", "card_id", "isbns")