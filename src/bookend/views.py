from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import *
from django.http import FileResponse, HttpResponse
from django.db.models import Sum
from django.core.files import File

from api.ISBNQuery import ISBNQuery
from api.Barcodes import Barcodes
from api.CoverGeneration import gen_cover
from api.StickerWizard import StickerWizard

from django_tables2 import SingleTableView, LazyPaginator

from .models import AppMetadata, Stats
from .tables import BookTable, UserBookTable, UserTable, StatsTable
import zipfile
import time
import csv
import glob, os
import requests
from io import BytesIO



# Create your views here.
class MyTableClass(SingleTableView):
    table_class = BookTable
    queryset = Book.objects.all()
    template_name = "tables/book-catalog.html"
    SingleTableView.table_pagination = False

class UserTableClass(SingleTableView):
    table_class = UserTable
    queryset = User.objects.all()
    template_name = "tables/user-catalog.html"
    SingleTableView.table_pagination = False

def get_stats_obj() -> Stats:
    if len(Stats.objects.all()) == 0:
        mStats = Stats()
        mStats.save()
    return Stats.objects.all()[0]

def get_app_title():
    if len(AppMetadata.objects.all()) == 0:
        mMetadata = AppMetadata()
        mMetadata.save()
    return AppMetadata.objects.all()[0].app_name

def update_app_title(new_title: str):
    if len(AppMetadata.objects.all()) == 0:
        mMetadata = AppMetadata()
        mMetadata.app_name = new_title
        mMetadata.save()
    else:
        mMetadata = AppMetadata.objects.all()[0]
        mMetadata.app_name = new_title
        mMetadata.save()

def base_render(request, template_name, context=None):
    if context is None:
        context = {}
    return render(request, template_name, {**context, **{"APP_TITLE": get_app_title()}})
def update_isbn_image(mBook: Book):
    mIsbn = mBook.isbn

    rv = Barcodes().gen_image(mIsbn)
    mBook.isbn_image.save(f"{mIsbn}.png", File(rv))

def update_cover_image(mBook: Book):
    print(f"mBook.thumbnail: {mBook.thumbnail}")
    if mBook.thumbnail != None and len(mBook.thumbnail) > 0:
        print("updating thumbnail image")
        response = requests.get(mBook.thumbnail)
        rv = BytesIO(response.content)
        mBook.thumbnail_image.save(f"{mBook.isbn}.png", File(rv))
    if mBook.thumbnail == None or len(mBook.thumbnail) == 0:
        title_list = str(mBook.title).split(" ")
        initials = [title_list[0][0]]
        if len(title_list) >= 2:
            initials.append(title_list[-1][0])
        rv = gen_cover(initials)
        mBook.thumbnail_image.save(f"{mBook.isbn}.png", File(rv))
def update_user_barcode_image(mUser: User):
    userId = mUser.card_id
    rv = Barcodes().gen_image(userId)
    mUser.card_id_image.save(f"{userId}.png", File(rv))

def home(request):
    checkInForm = CheckInForm()
    checkOutForm = CheckOutForm()
    return base_render(request, "pages/home.html", {"checkInForm": checkInForm,
                                                 "checkOutForm": checkOutForm})
def kiosk(request):
    checkInForm = CheckInForm()
    checkOutForm = CheckOutForm()
    return base_render(request, "pages/kiosk.html", {"checkInForm": checkInForm,
                                                 "checkOutForm": checkOutForm})
def all_users(request):
    return base_render(request, 'pages/all-users.html', { "table": UserTable(User.objects.all())})


def user_details(request, card_id):
    print(f"user details for card_id: {card_id}")
    mUser = get_object_or_404(User, card_id=card_id)

    if request.method == "POST":
        user_name_form = UserDetailsNameForm(request.POST)
        user_isbns_formset = ISBNFormSet(request.POST, prefix='isbns')
        user_details_form = UserDetailsForm(request.POST, instance=mUser) # only has the card_id

        if user_name_form.is_valid() and user_isbns_formset.is_valid() and user_details_form.is_valid():
            if card_id != user_details_form.cleaned_data['card_id']:
                if len(User.objects.filter(card_id=user_details_form.cleaned_data['card_id'])) == 0:
                    print(f"found no existing user with desired card id {user_details_form.cleaned_data['card_id']}")
                    update_user_barcode_image(mUser)
                    user_details_form.save()

                else:
                    print(f"existing user with card id {user_details_form.cleaned_data['card_id']} found, not going to change card_id")
                    messages.info(request, f"There is already a user with library card number {user_details_form.cleaned_data['card_id']}")
            new_isbns_list = []
            for isbn_form in user_isbns_formset:
                if isbn_form.cleaned_data and isbn_form.cleaned_data['isbn'] != "":
                    new_isbns_list.append(isbn_form.cleaned_data['isbn'])
                    print(isbn_form.cleaned_data['isbn'])
            mUser.isbns = new_isbns_list
            mUser.name = user_name_form.cleaned_data['name']

            mUser.save()

            messages.info(request, f"Updated details for {mUser.name}")
            return redirect("userDetails", card_id=user_details_form.cleaned_data["card_id"])

    mUser = get_object_or_404(User, card_id=card_id)

    user_name_form = UserDetailsNameForm(initial={"name": mUser.name})
    user_details_form = UserDetailsForm(instance=mUser)  # only has the card_id

    initial_isbns = [{'isbn': isbn} for isbn in mUser.isbns]
    user_isbns_formset = ISBNFormSet(prefix='isbns', initial=initial_isbns)

    return base_render(request, 'pages/user-details.html',{
        'user_name_form': user_name_form,
        'user_isbns_formset': user_isbns_formset,
        'user_details_form': user_details_form,
    })

def new_user(request):
    if request.method == "POST":
        newUserForm = NewUserForm(request.POST)
        if newUserForm.is_valid():
            existingUsers = User.objects.filter(card_id=newUserForm.cleaned_data["card_id"])
            if len(existingUsers) > 0:
                messages.info(request, "User with Id: {} already exists".format(newUserForm.cleaned_data["card_id"]))
            else:
                newUserForm.save()
                mUser = User.objects.filter(card_id=newUserForm.cleaned_data["card_id"])[0]
                update_user_barcode_image(mUser)
                messages.info(request, "{}'s profile has been created".format(newUserForm.cleaned_data["name"]))
    newUserForm = NewUserForm()
    return base_render(request, "pages/new-user.html", {"form": newUserForm })

def remove_user(request):
    if request.method == "POST":
        removeUserForm = RemoveUserForm(request.POST)
        if removeUserForm.is_valid():
            existingUsers = User.objects.filter(card_id=removeUserForm.cleaned_data["card_id"])
            if len(existingUsers) > 0:
                mUser = existingUsers[0]
                isbns_to_remove = list(mUser.isbns)
                print(f"checked out books to remove: {isbns_to_remove}")
                for mIsbn in isbns_to_remove:
                    if len(Book.objects.filter(isbn=mIsbn)) > 0:
                        mBook = Book.objects.filter(isbn=mIsbn)[0]
                        mBook.checkedOut -= 1
                        mBook.save()
                    mUser.isbns.remove(mIsbn)
                    mUser.save()
                    print(f"removed {mIsbn}. mUser isbns: {mUser.isbns}")

                messages.info(request, "Deleted user {}".format(mUser.name))
                print(f"deleted user {mUser.name}:{mUser.card_id}")
                mUser.delete()
            else:
                messages.info(request, "No user with ID {}".format(removeUserForm.cleaned_data["card_id"]))
    removeUserForm = RemoveUserForm()
    return base_render(request, "pages/remove-user.html", {"form": removeUserForm })


def user_books(request):
    if request.method == "POST":
        userBooksForm = ViewUserBooksForm(request.POST)
        if userBooksForm.is_valid():
            existingUsers = User.objects.filter(card_id=userBooksForm.cleaned_data["card_id"])
            if len(existingUsers) > 0:
                mUser = existingUsers[0]
                mBookList = []
                for misbn in mUser.isbns:
                    if len(Book.objects.filter(isbn=misbn)) > 0:
                        mBook = Book.objects.filter(isbn=misbn)[0]
                        mBookList.append(mBook)

                mTable = UserBookTable(mBookList)

                return base_render(request, "pages/user-books.html", {"form": userBooksForm,
                                                                  "table": mTable })
            else:
                messages.info(request, f"No user found for ID {userBooksForm.cleaned_data['card_id']}")
        else:
            print("form is invalid")


    return base_render(request, "pages/user-books.html", {"form": ViewUserBooksForm()})

def new_book(request):

    manual_book_info_form = ManualAddBookForm()
    manual_book_title_form = BookDetailsTitleForm()
    author_formset = AuthorFormSet(prefix='authors')
    tag_formset = TagFormSet(prefix='tags')

    return base_render(request, "pages/new-book.html", {
        "ISBNForm": ISBNAddBookForm(),
        "manual_book_info_form": manual_book_info_form,
        "manual_book_title_form": manual_book_title_form,
        "author_formset": author_formset,
        "tag_formset": tag_formset,

    })

def new_book_manual(request):
    if request.method == "POST":
        info_form = ManualAddBookForm(request.POST)
        title_form = BookDetailsTitleForm(request.POST)
        author_formset = AuthorFormSet(request.POST, prefix='authors')
        tag_formset = TagFormSet(request.POST, prefix='tags')

        if info_form.is_valid() and title_form.is_valid() and author_formset.is_valid() and tag_formset.is_valid():
            print(title_form.cleaned_data["title"])

            existingBookList = Book.objects.filter(isbn=info_form.cleaned_data["isbn"])
            if len(existingBookList) > 0:
                mBook = existingBookList[0]
                mBook.quantity += 1
                messages.info(request, "You now have {} copies of {}".format(mBook.quantity, mBook.title))
                mBook.save()
            else:
                info_form.save()
                mBook = Book.objects.filter(isbn=info_form.cleaned_data["isbn"])[0]
                mBook.title = title_form.cleaned_data["title"]
                author_list = []
                for author_form in author_formset:
                    if author_form.cleaned_data and author_form.cleaned_data['name'] != "":
                        author_list.append(author_form.cleaned_data['name'])
                        print(author_form.cleaned_data['name'])
                mBook.authors = author_list
                tag_list = []
                for tag_form in tag_formset:
                    if tag_form.cleaned_data and tag_form.cleaned_data['name'] != "":
                        tag_list.append(tag_form.cleaned_data['name'])
                mBook.tags = tag_list
                mBook.save()
                update_isbn_image(mBook)
                update_cover_image(mBook)

                messages.info(request, "Added {} to your library".format(title_form.cleaned_data["title"]))


    return redirect("newBook",)

def new_book_isbn(request):
    if request.method == "POST":
        bookForm = ISBNAddBookForm(request.POST)
        if bookForm.is_valid():
            print(bookForm.cleaned_data["isbn"])
            bookDict = ISBNQuery().query(bookForm.cleaned_data["isbn"])
            if bookDict is not None:
                bookDict = {i:bookDict[i] for i in bookDict if i!='categories'}

            if bookDict is None:
                messages.info(request, "Error, could not add book")
            else:

                book = Book.objects.filter(isbn=bookForm.cleaned_data["isbn"])
                if len(book) == 0:
                    book = Book(**bookDict)
                    messages.info(request, "Added {} to your library".format(bookDict["title"]))
                    print(bookDict)
                    print(f"Added {bookDict['title']} to your library")
                    book.quantity = 1
                    book.authors = [a[0] for a in bookDict["authors"]]
                    book.save()
                    mBook = Book.objects.filter(isbn=book.isbn)[0]
                    update_isbn_image(mBook)
                    update_cover_image(mBook)
                else:
                    book[0].quantity += 1
                    book[0].save()
                    messages.info(request, "You now have {} copies of {}".format(book[0].quantity, book[0].title))

    return redirect("newBook", )

def remove_book(request):
    if request.method == "POST":
        removeBookForm = RemoveBookForm(request.POST)
        if removeBookForm.is_valid():
            existingBooks = Book.objects.filter(isbn=removeBookForm.cleaned_data["isbn"])
            if len(existingBooks) > 0:
                mBook = existingBooks[0]
                print(f"removed {mBook.title}")
                messages.info(request, "Deleted {}".format(mBook.title))

                mBook.delete()
            else:
                messages.info(request, "No book with ISBN {}".format(removeBookForm.cleaned_data["isbn"]))
    removeBookForm = RemoveBookForm()
    return base_render(request, "pages/remove-book.html", {"form": removeBookForm })

def book_details(request, isbn):
    print("book details")
    mBook = get_object_or_404(Book, isbn=isbn)

    if request.method == 'POST':
        book_info_form = BookDetailsContdForm(request.POST, instance=mBook)
        book_title_form = BookDetailsTitleForm(request.POST, instance=mBook)
        author_formset = AuthorFormSet(request.POST, prefix='authors')
        tag_formset = TagFormSet(request.POST, prefix='tags')

        print(f"book_info_form.is_valid()? {book_info_form.is_valid()}")
        print(f"book_title_form.is_valid()? {book_title_form.is_valid()}")
        print(f"author_formset.is_valid()? {author_formset.is_valid()}")
        print(f"tag_formset.is_valid()? {tag_formset.is_valid()}")

        print(f"author_formset.errors: {author_formset.errors}")
        print(f"book_info_form.errors: {book_info_form.errors}")

        if book_info_form.is_valid() and book_title_form.is_valid() and author_formset.is_valid() and tag_formset.is_valid():
            update_cover_image(mBook)
            if isbn != book_info_form.cleaned_data["isbn"]:
                if len(Book.objects.filter(isbn=book_info_form.cleaned_data["isbn"])) == 0:

                    book_info_form.save()
                    update_isbn_image(mBook)


                else:
                    messages.info(request, f"Existing book with the ISBN {book_info_form.cleaned_data['isbn']}, not updating this book's ISBN")

            # Save authors and tags to the book instance
            mBook.authors.clear()
            print("going to update author list")
            new_author_list = []
            for author_form in author_formset:
                if author_form.cleaned_data and author_form.cleaned_data['name'] != "":
                    new_author_list.append(author_form.cleaned_data['name'])
                    print(author_form.cleaned_data['name'])
            mBook.authors = new_author_list

            mBook.tags.clear()
            new_tag_list = []
            for tag_form in tag_formset:
                if tag_form.cleaned_data and tag_form.cleaned_data['name'] != "":
                    new_tag_list.append(tag_form.cleaned_data['name'])
            mBook.tags = new_tag_list

            mBook.save()
            messages.info(request, f"Updated {mBook.title}")

            return redirect('bookDetails', isbn=book_info_form.cleaned_data['isbn'])
        else:
            messages.info(request, f"Error updating {mBook.title}, invalid information")


    mBook = get_object_or_404(Book, isbn=isbn)
    book_info_form = BookDetailsContdForm(instance=mBook)
    book_title_form = BookDetailsTitleForm(instance=mBook)

    initial_authors = [{'name': author} for author in mBook.authors]
    author_formset = AuthorFormSet(prefix='authors', initial=initial_authors)
    initial_tags = [{'name': tag} for tag in mBook.tags]
    tag_formset = TagFormSet(prefix='tags', initial=initial_tags)

    return base_render(request, 'pages/book-details.html', {
        'book_info_form': book_info_form,
        'book_title_form': book_title_form,
        'author_formset': author_formset,
        'tag_formset': tag_formset,
    })

def check_in(request):
    if request.method == "POST":
        checkInForm = CheckInForm(request.POST)
        if checkInForm.is_valid():
            print("form is valid")
            print(checkInForm.cleaned_data["card_id"])
            print(checkInForm.cleaned_data["isbn"])
            desiredBookList = Book.objects.filter(isbn=checkInForm.cleaned_data["isbn"])
            print("desiredBookList: {}".format(desiredBookList))
            if len(desiredBookList) > 0:
                mBook = desiredBookList[0]
                userList = User.objects.filter(card_id=checkInForm.cleaned_data["card_id"])
                if len(userList) > 0:
                    mUser = userList[0]
                    if mUser.isbns.__contains__(checkInForm.cleaned_data["isbn"]):
                        mUser.isbns.remove(mBook.isbn)
                        mUser.save()
                        mBook.checkedOut -= 1
                        mBook.save()
                        messages.info(request, "Returned {}".format(mBook.title))
                        print("Returned {}".format(mBook.title))
                    else:
                        messages.info(request, "{} has not checked out {}".format(mUser.name, mBook.title))
                else:
                    messages.info(request, "Invalid library card")
                    print("invalid card id")
            else:
                messages.info(request, "Could not find ISBN")
                print("book with entered ISBN is not in your library")
        else:
            print("form is invalid")
    if request.META['HTTP_REFERER'][-2:] == '/l':
        return redirect("kiosk")
    else:
        print("redirecting to home")
        return redirect("home")

def check_out(request):
    if request.method == "POST":
        checkOutForm = CheckOutForm(request.POST)
        if checkOutForm.is_valid():
            print("form is valid")
            print(checkOutForm.cleaned_data["card_id"])
            print(checkOutForm.cleaned_data["isbn"])
            desiredBookList = Book.objects.filter(isbn=checkOutForm.cleaned_data["isbn"])
            print("desiredBookList: {}".format(desiredBookList))
            if len(desiredBookList) > 0:
                if desiredBookList[0].quantity > 0:
                    userList = User.objects.filter(card_id=checkOutForm.cleaned_data["card_id"])
                    if len(userList) > 0:
                        userList[0].isbns += [checkOutForm.cleaned_data["isbn"]]
                        userList[0].save()
                        desiredBookList[0].checkedOut += 1
                        desiredBookList[0].total_checked_out += 1
                        mStats = get_stats_obj()
                        mStats.total_checked_out += 1
                        mStats.most_recent_checked_out += [checkOutForm.cleaned_data["isbn"]]
                        if len(mStats.most_recent_checked_out) > 5:
                            mStats.most_recent_checked_out.pop(0)
                        mStats.save()
                        desiredBookList[0].save()
                        messages.info(request, "{} checked out {}".format(userList[0].name, desiredBookList[0].title))
                        print("{} checked out {}".format(userList[0].name, desiredBookList[0].title))
                    else:
                        messages.info(request, "Invalid library card")
                        print("invalid card id")
                else:
                    messages.info(request, "All copies of {} are already checked out".format(desiredBookList[0].title))
            else:
                messages.info(request, "Could not find ISBN")
                print("book with entered ISBN is not in your library")
        else:
            print("form is invalid")
    if request.META['HTTP_REFERER'][-2:] == '/l':
        return redirect("kiosk")
    else:
        print("redirecting to home")
        return redirect("home")

def catalog(request):
    form = SearchForm(request.POST)
    ordered_by = 'title'
    if request.method == "POST":
        if form.is_valid():
            raw = form.cleaned_data['terms']
            query = ''
            for ch in raw:
                query += '[' + ch.upper() + ch.lower() + ']'
            query_regex = r'.*' + query + r'.*'
            results = (
                    Book.objects.filter(title__regex=query_regex)
                    | Book.objects.filter(authors__regex=query_regex)
                    | Book.objects.filter(isbn__regex=query_regex)
                    | Book.objects.filter(tags__regex=query_regex)
                    ).order_by("title")

            print(f"results: {results}")
            if len(results) > 0:
                num_results = results.aggregate(Sum("quantity"))["quantity__sum"]
            else:
                num_results = 0
            return base_render(request, "pages/catalog.html", {"form": form,
                                                           "table": BookTable(results),
                                                            "num_results": num_results
                                                            })
    else:
        ordered_by = request.GET.get('sort', 'title')
        print(f"what is the sorted order? {ordered_by}")
    if len(Book.objects.all()) > 0:
        num_results = Book.objects.all().aggregate(Sum("quantity"))["quantity__sum"]
    else:
        num_results = 0

    return base_render(request, "pages/catalog.html", {"form": SearchForm(),
                                                    "table":BookTable(Book.objects.all().order_by(ordered_by)),
                                                    "num_results": num_results})

def stats(request):
    # if request.method == "POST":
    # Recalculate all stats
    # BOOKS FIRST
    mStats = get_stats_obj()
    mStats.total_books = 0
    mStats.total_checked_out = 0
    mStats.most_checked_out_books = [b.isbn for b in Book.objects.order_by("-total_checked_out")[:5]]
    mStats.books_with_most_copies = [b.isbn for b in Book.objects.order_by("-quantity")[:5]]
    mStats.newest_books = [b.isbn for b in Book.objects.order_by("-date_added")[:5]]
    book_list = Book.objects.all()
    if book_list != None and len(book_list) > 0:
        for b in book_list:
            # TOTAL BOOKS
            mStats.total_books += b.quantity
            # TOTAL CHECKED OUT
            mStats.total_checked_out += b.checkedOut


    # USERS SECOND
    mStats.total_users = 0
    mStats.newest_users = [u.card_id for u in User.objects.order_by("-date_added")[:5]]
    user_list = User.objects.all()
    if user_list != None and len(user_list) > 0:
        for u in user_list:
            # TOTAL USERS
            mStats.total_users += 1

    mStats.save()

    # return base_render(request, "pages/stats.html", {"table": StatsTable([get_stats_obj()])})
    return base_render(request, "pages/stats.html", {"table": StatsTable([get_stats_obj()])})
def report_helper():
    print("Running report helper")
    book_list = []
    book_keys = ("title", "authors", "isbn", "quantity", "checkedOut")
    for mBook in Book.objects.all():
        bookDict = {d: mBook.__dict__[d] for d in book_keys}
        book_list.append(bookDict)

    with open("all_books.csv", "w", newline="") as f:
        dict_writer = csv.DictWriter(f, book_keys)
        dict_writer.writeheader()
        dict_writer.writerows(book_list)

    user_list = []
    user_keys = ("name", "card_id", "title", "isbn")
    for mUser in User.objects.all():
        print(f"Number of books checked out to {mUser.name}: {mUser.isbns}")
        if len(mUser.isbns) == 0:
            userDict = {"name": mUser.name, "card_id": mUser.card_id, "title": "", "isbn": ""}
            user_list.append(userDict)
        else:
            for index, misbn in enumerate(mUser.isbns):
                if len(mUser.isbns) == 0:
                    userDict = {"name": mUser.name, "card_id": mUser.card_id, "title": "", "isbn": ""}
                if len(Book.objects.filter(isbn=misbn)) > 0:
                    mBook = Book.objects.filter(isbn=misbn)[0]
                    userDict = {"name": mUser.name, "card_id": mUser.card_id, "title": mBook.title, "isbn": mBook.isbn}
                else:
                    userDict = {"name": mUser.name, "card_id": mUser.card_id, "title": "INVALID_ISBN", "isbn": misbn}
                user_list.append(userDict)

    with open("all_users.csv", "w", newline="") as f:
        dict_writer = csv.DictWriter(f, user_keys)
        dict_writer.writeheader()
        dict_writer.writerows(user_list)

    return book_list, user_list

def books_report(request):
    book_list, user_list = report_helper()

    return FileResponse(open("all_books.csv", "rb"), as_attachment=False)

def users_report(request):
    book_list, user_list = report_helper()

    return FileResponse(open("all_users.csv", "rb"), as_attachment=False)

def download_report(request):
    book_list, user_list = report_helper()

    with zipfile.ZipFile("report.zip", mode="w") as archive:
        archive.write("all_books.csv")
        archive.write("all_users.csv")

    return FileResponse(open("report.zip", "rb"), as_attachment=True)

def import_csv(request):
    if request.method == "POST":
        print("in post method")
        uploadForm = UploadFileForm(request.POST, request.FILES)
        print("next")
        if uploadForm.is_valid():
            m_file = request.FILES["file"]

            with open('imported_data.csv', 'wb+') as destination:
                for chunk in m_file.chunks():
                    destination.write(chunk)

            with open("imported_data.csv", "r") as m_csv:
                m_csv.readline()
                m_csv.readline()
                for line in m_csv:
                    s_line = line.strip().strip("\"").split(",")
                    print(f"s_line: {s_line}")

                    if not s_line[-2].isnumeric() or int(s_line[-2]) > 100:
                        quantity=1
                    else:
                        quantity = s_line[-2]

                    isbn = s_line[-3]
                    authors = s_line[-5:-3]
                    title = ",".join(str(e) for e in s_line[-6::-1][::-1])

                    book = Book.objects.filter(isbn=isbn)
                    if len(book) > 0:
                        print(f"book with ISBN {isbn} already in library")
                        print(book)
                        continue

                    bookDict = ISBNQuery().lookup(isbn)
                    time.sleep(3)

                    if bookDict is None:
                        bookDict = {"title": title,
                                  "authors": authors,
                                  "isbn": isbn,
                                  "quantity": quantity,
                                  }
                    else:
                        bookDict["title"] = title
                        bookDict["authors"] = authors
                        bookDict["isbn"] = isbn
                        bookDict["quantity"] = quantity

                    book = Book(**bookDict)
                    book.quantity = quantity
                    book.save()

        else:
            messages.info(request, "Invalid form")

    return base_render(request, "pages/import-csv.html", {"form": UploadFileForm()})

def sticker_wizard(request):
    if request.method == "POST":
        form = StickerWizardForm(request.POST)
        if form.is_valid():
            sticker_imgs = glob.glob('api/sticker_wizard_imgs/*')
            for s in sticker_imgs:
                os.remove(s)
            isbn_list = form.cleaned_data['isbn_list'].replace(" ", "").replace("\n", "").replace("\r", "").split(",")
            for isbn in isbn_list:
                if len(Book.objects.filter(isbn=isbn)) == 0:
                    messages.info(request, f"ISBN {isbn} does not exist in your library")
                    return base_render(request, "pages/sticker-wizard.html", {"form": form})

            StickerWizard().AveryTemplate5160(isbn_list, "isbn_template.pdf")

            return FileResponse(open("isbn_template.pdf", "rb"), as_attachment=True)

    return base_render(request, "pages/sticker-wizard.html", {"form": StickerWizardForm()})


def settings(request):
    if request.method == "POST":
        name_form = AppNameForm(request.POST)
        if name_form.is_valid():
            update_app_title(name_form.cleaned_data['name'])

    return base_render(request, "pages/settings.html", {"form": AppNameForm(initial={"name": get_app_title()})})

def clean_author_fields(request):
    for mBook in Book.objects.all():
        list_authors = list(mBook.authors)
        for author in list_authors:
            if author == "":
                mBook.authors.remove(author)
                print(f"removing author {author}")
        mBook.save()

    messages.info(request, "Cleaned author field for all books")

    return redirect("tools")

def regenerate_images_helper():
    book_barcodes = glob.glob('website/static/data/book_isbn_images/*')
    book_covers = glob.glob('website/static/data/book_cover_images/*')
    card_files = glob.glob('website/static/data/card_id_images/*')
    for f in book_barcodes:
        os.remove(f)
    for f in book_covers:
        os.remove(f)
    for f in card_files:
        os.remove(f)

    for mBook in Book.objects.all():
        update_isbn_image(mBook)
        update_cover_image(mBook)

    for mUser in User.objects.all():
        update_user_barcode_image(mUser)

    print("regenerated barcodes for all objects")

def generate_barcodes(request):
    regenerate_images_helper()

    messages.info(request, "Generated ISBN and library card barcodes for objects in the database")

    return redirect("settings")