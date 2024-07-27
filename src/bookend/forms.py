from django.forms import ModelForm, DateInput, TextInput, ImageField
from django import forms
from django.forms import formset_factory, BaseFormSet
from django.utils.html import format_html

from .models import Book, User

"""
All post forms should live here. Separate post forms for each view.
"""

class PictureWidget(forms.widgets.Widget):
    def render(self, name, value, attrs=None, **kwargs):
        print(f"{name}, {value}, {attrs}, {kwargs}")
        return format_html('<img class="text-center" src="/{}" />', value)


class ManualAddBookForm(ModelForm):
    class Meta:
        model = Book
        fields = ("isbn", "quantity", "checkedOut")
        labels = {
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

class UserDetailsISBNForm(forms.Form):
    isbn = forms.CharField(label="ISBN", max_length=13, required=False)

class BaseISBNFormSet(BaseFormSet):
    def clean(self):
        if any(self.errors):
            return
        non_empty_forms = [form for form in self.forms if form.cleaned_data.get('isbn')]
        for form in non_empty_forms:
            if self.can_delete and self._should_delete_form(form):
                continue

ISBNFormSet = formset_factory(UserDetailsISBNForm, formset=BaseISBNFormSet, extra=1)

class UserDetailsNameForm(forms.Form):
    name = forms.CharField(label="Name")

class UserDetailsForm(ModelForm):
    card_id_image = ImageField(widget=PictureWidget(), label="")

    class Meta:
        model = User
        exclude = ("isbns", "name")
        labels = {
            "card_id": "Library Card Number",
        }

class BookDetailsTitleForm(ModelForm):
    class Meta:
        model = Book
        fields = {"title"}

class BookDetailsAuthorForm(forms.Form):
    name = forms.CharField(label='Author', required=False)

class BaseAuthorFormSet(BaseFormSet):
    def clean(self):
        if any(self.errors):
            return
        non_empty_forms = [form for form in self.forms if form.cleaned_data.get('name')]
        for form in non_empty_forms:
            if self.can_delete and self._should_delete_form(form):
                continue

class BookDetailsTagForm(forms.Form):
    name = forms.CharField(label='Tag', required=False)

class BaseTagFormSet(BaseFormSet):
    def clean(self):
        if any(self.errors):
            return
        non_empty_forms = [form for form in self.forms if form.cleaned_data.get('name')]
        for form in non_empty_forms:
            if self.can_delete and self._should_delete_form(form):
                continue

AuthorFormSet = formset_factory(BookDetailsAuthorForm, formset=BaseAuthorFormSet, extra=1)
TagFormSet = formset_factory(BookDetailsTagForm, formset=BaseTagFormSet, extra=1)


class BookDetailsContdForm(ModelForm):
    isbn_image = ImageField(widget=PictureWidget(), label="")
    thumbnail_image = ImageField(widget=PictureWidget(), label="")

    class Meta:
        model = Book
        exclude = ('title', 'authors', 'tags')

        widgets = {
            "publishedDate": DateInput(attrs={"type:": "selectdate"}),
            # "averageRating": TextInput(attrs={"type": "float", "min": "0", "max": "5"}),

        }
        labels = {
            "isbn": 'ISBN',
            "thumbnail": 'Cover Image URL',
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

class AppNameForm(forms.Form):
    name = forms.CharField(label="Website name")