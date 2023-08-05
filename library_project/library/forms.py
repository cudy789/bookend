from django.forms import ModelForm, DateInput, TextInput
from django import forms
from .models import Book, User

"""
All post forms should live here. Separate post forms for each view.
"""
class ManualAddBookForm(ModelForm):
    class Meta:
        model = Book
        fields = "__all__"
        widgets = {
            "publishedDate": DateInput(attrs={"type:": "date"}),
            "averageRating": TextInput(attrs={"type": "number", "min": "0", "max": "5"})
        }

class ISBNAddBookForm(ModelForm):
    class Meta:
        model = Book
        fields = ("isbn",)
        labels = {
            "isbn": "ISBN"
        }
        widgets = {"isbn": forms.TextInput(attrs={'autofocus': True})}

class CheckInForm(forms.Form):
    card_id = forms.CharField(label="Library Card Number")
    isbn = forms.CharField(label="ISBN")
    class Meta:
        fields = ["card_id", "isbn",]


class CheckOutForm(forms.Form):
    card_id = forms.CharField(label="Library Card Number")
    isbn = forms.CharField(label="ISBN")
    class Meta:
        fields = ["card_id", "isbn",]


class NewUserForm(ModelForm):
    class Meta:
        model = User
        fields = ("name", "card_id")
        labels = {
            "card_id": "Library Card Number"
        }

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
            "query": "title, author, category, ISBN"
        }