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

class BookTable(tables.Table):
    thumbnail = ImageColumn('Cover')
    authors = AuthorColumn('Authors')
    categories = CategoriesColumn('Categories')
    class Meta:
        model = Book
        attrs = {"class": "table",
                 'thead': {
                     'class': 'thead-dark'
                 }}
        fields = ("thumbnail", "title", "authors", "categories", "quantity", "checkedOut", "isbn")

class UserBookTable(tables.Table):
    thumbnail = ImageColumn('Thumbnail')
    authors = AuthorColumn('Authors')
    class Meta:
        model = Book
        attrs = {"class": "table",
                 'thead': {
                     'class': 'thead-dark'
                 }}
        fields = ("thumbnail", "title", "authors")

class UserTable(tables.Table):
    class Meta:
        model = User
        attrs = {"class": "table",
                 'thead': {
                     'class': 'thead-dark'
                 }}
        fields = ("name", "card_id")