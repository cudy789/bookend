import django_tables2 as tables
from django.utils.html import format_html
from .models import Book, User, Stats

class ImageColumn(tables.Column):
    def render(self, value):
        print(f"VALUE: {value}")
        return format_html(f'<img src="/{value}" />',)

class AuthorColumn(tables.Column):
    def render(self, value):
        res = ''
        for i, author in enumerate(value):
            if i == 0:
                res += author
            else:
                res += ', ' + author
        return res

class TagsColumn(tables.Column):
    def render(self, value):
        res = ''
        for i, tag in enumerate(value):
            if i == 0:
                res += tag
            else:
                res += ', ' + tag
            print(i, tag)
            # res += str(tag) + ', '
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
                if len(Book.objects.filter(isbn=isbn)) > 0:
                    isbn = Book.objects.filter(isbn=isbn)[0].title
                else:
                    isbn = f"invalidISBN:{isbn}"
                if len(value) > 1 and i < len(value) - 1:
                    isbn += ", "
                # isbn = "its a book!"
            res += str(isbn)
        if len(res) > 0 and res[:-2] == ", ":
            return res[:-1]
        else:
            return res

class BookTitleLinkColumn(tables.Column):
    def __init__(self, *args, additional_key=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.additional_key = additional_key

    def render(self, value):
        res = '<ol>'
        for i, isbn in enumerate(value):
            if type(isbn) is str and len(isbn) > 0:
                if len(Book.objects.filter(isbn=isbn)) > 0:
                    mBook = Book.objects.filter(isbn=isbn)[0]
                    s_title = mBook.title
                    additional_text = ""
                    if self.additional_key != None:
                        if self.additional_key[0] == 'date_added':
                            additional_text = f"{self.additional_key[1]}: {getattr(mBook, self.additional_key[0]).strftime('%d-%m-%Y')}"
                        else:
                            additional_text = f"{self.additional_key[1]}: {getattr(mBook, self.additional_key[0])}"

                    title = '<li><a href="library/book/{}">{}</a>{}</li>'.format(isbn, s_title, additional_text)
                else:
                    title = f"invalidISBN:{isbn}"
                res += title
        res += '</ol>'
        return format_html(res)

class UserNameLink(tables.Column):
    def __init__(self, *args, additional_key=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.additional_key = additional_key

    def render(self, value):
        res = '<ol>'
        for i, card_id in enumerate(value):
            if type(card_id) is str and len(card_id) > 0:
                if len(User.objects.filter(card_id=card_id)) > 0:
                    mUser = User.objects.filter(card_id=card_id)[0]
                    s_name = mUser.name
                    additional_text = ""
                    if self.additional_key != None:
                        if self.additional_key[0] == 'date_added':
                            additional_text = f"{self.additional_key[1]}: {getattr(mUser, self.additional_key[0]).strftime('%d-%m-%Y')}"
                        else:
                            additional_text = f"{self.additional_key[1]}: {getattr(mUser, self.additional_key[0])}"

                    name = '<li><a href="/user/{}">{}</a>{}</li>'.format(card_id, s_name, additional_text)
                else:
                    name = f"invalidCardID:{card_id}"
                res += name
        res += '</ol>'
        return format_html(res)

class UserColumnLink(tables.Column):
    def render(self, value):
        return format_html('<a href="users/{}">{}</a>', value, value)


# class ISBNColumn(tables.Column):
#     def render(self, value):
#         res = ''
#         if type(isbn) is str and len(isbn) > 0:
#             # isbn = author[0]
#             print(isbn)
#         res += str(isbn) + ', '
#
#         if len(res) > 0 and res[:-2] == ", ":
#             return res[:-1]
#         else:
#             return res

class LinkISBNColumn(tables.Column):
    def render(self, value):
        return format_html('<a href="book/{}">{}</a>', value, value)

class StatsTable(tables.Table):
    most_checked_out_books = BookTitleLinkColumn("Most checked out books ever", additional_key=["total_checked_out", ""])
    most_recent_checked_out = BookTitleLinkColumn()
    newest_books = BookTitleLinkColumn(additional_key=["date_added", ""])
    books_with_most_copies = BookTitleLinkColumn(additional_key=["quantity", ""])
    newest_users = UserNameLink(additional_key=["date_added", ""])
    class Meta:
        model = Stats
        attrs = {"class": "table",
                 'thead': {
                     'class': 'thead-dark'
                 }}
        exclude = ("id",)

class BookTable(tables.Table):
    thumbnail_image = ImageColumn('Cover')
    authors = AuthorColumn('Authors')
    isbn = LinkISBNColumn('ISBN')
    tags = TagsColumn('Tags')
    class Meta:
        model = Book
        attrs = {"class": "table",
                 'thead': {
                     'class': 'thead-dark'
                 }}
        fields = ("thumbnail_image", "title", "authors", "tags", "quantity", "checkedOut", "isbn")

class UserBookTable(tables.Table):
    thumbnail_image = ImageColumn('Cover')
    authors = AuthorColumn('Authors')
    class Meta:
        model = Book
        attrs = {"class": "table",
                 'thead': {
                     'class': 'thead-dark'
                 }}
        fields = ("thumbnail_image", "title", "authors", "isbn")

class UserTable(tables.Table):
    isbns = BookTitleLinkColumn('Books', additional_key=["isbn", ""])
    card_id = UserColumnLink('Card Number')

    class Meta:
        model = User
        attrs = {"class": "table",
                 'thead': {
                     'class': 'thead-dark'
                 }}
        fields = ("name", "card_id", "isbns")