from django.forms import ModelForm, DateInput, TextInput, ImageField
from django import forms
from django.utils.html import format_html

from .models import Book, User

"""
All post forms should live here. Separate post forms for each view.
"""

class PictureWidget(forms.widgets.Widget):
    def render(self, name, value, attrs=None, **kwargs):
        print(f"{name}, {value}, {attrs}, {kwargs}")
        return format_html('<img src="{}" />', value)
        # html =  Template("""<img src="$link"/>""")
        # return mark_safe(html.substitute(link=value))
class ManualAddBookForm(ModelForm):
    class Meta:
        model = Book
        # fields = "__all__",
        fields = ("title", "authors", "tags", "isbn", "quantity", "checkedOut")
        labels = {
            "authors": 'Authors - ["author 1", "author 2", ... ]',
            "tags": 'Tags - ["tag 1", "tag 2", ... ]',
            "isbn": "ISBN",
        }


class ISBNAddBookForm(ModelForm):
    class Meta:
        model = Book
        fields = ("isbn",)
        labels = {
            "isbn": "ISBN"
        }
        widgets = {"isbn": forms.TextInput(attrs={'autofocus': True})}

class RemoveBookForm(ModelForm):
    class Meta:
        model = Book
        fields = ("isbn",)
        labels = {
            "isbn": "ISBN"
        }
        widgets = {"isbn": forms.TextInput(attrs={'autofocus': True})}

class CheckInForm(forms.Form):
    card_id = forms.CharField(label="Library Card Number",
                              widget=forms.TextInput(attrs={'id': 'card_id_checkin'}))
    isbn = forms.CharField(label="ISBN")
    class Meta:
        fields = ["card_id", "isbn",]



class CheckOutForm(forms.Form):
    card_id = forms.CharField(label="Library Card Number",
                              widget=forms.TextInput(attrs={'id': 'card_id_checkout'}))
    isbn = forms.CharField(label="ISBN")
    class Meta:
        fields = ["card_id", "isbn",]

class UserDetailsForm(ModelForm):
    card_id_image = ImageField(widget=PictureWidget(), label="")

    class Meta:
        model = User
        fields = "__all__"
        labels = {
            "card_id": "Library Card Number",
        }

class BookDetailsForm(ModelForm):
    isbn_image = ImageField(widget=PictureWidget(), label="")

    class Meta:
        model = Book
        fields = "__all__"
        widgets = {
            "publishedDate": DateInput(attrs={"type:": "selectdate"}),
            "averageRating": TextInput(attrs={"type": "number", "min": "0", "max": "5"}),

        }
        labels = {
            "authors": 'Authors - ["author 1", "author 2", ... ]',
            "tags": 'Tags - ["tag 1", "tag 2", ... ]',
            "isbn": "ISBN",
        }



class NewUserForm(ModelForm):
    class Meta:
        model = User
        fields = ("name", "card_id")
        labels = {
            "card_id": "Library Card Number"
        }
        widgets = {"name": forms.TextInput(attrs={'autofocus': True})}

class RemoveUserForm(ModelForm):
    class Meta:
        model = User
        fields = ("card_id",)
        labels = {
            "card_id": "Library Card Number"
        }
        widgets = {"card_id": forms.TextInput(attrs={'autofocus': True})}

class ViewUserBooksForm(forms.Form):
    card_id = forms.CharField(label="Library Card Number")
    class Meta:
        fields = ["card_id",]

class UploadFileForm(forms.Form):
    file = forms.FileField()

class SearchForm(forms.Form):
    terms = forms.CharField(label="Search terms", required=False, widget=forms.TextInput(attrs={'autofocus': True}))
    class Meta:
        fields = ("query")
        labels = {
            "query": "title, author, category, ISBN, tags"
        }