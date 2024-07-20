import barcode.errors
from django.shortcuts import render, redirect, get_object_or_404
from isbnlookup.isbnlookup import ISBNLookup
from django.contrib import messages
from .forms import *
from django.http import FileResponse, HttpResponse
from django.db.models import Sum
from django.core.files import File

from barcode import EAN13, ISBN13, ISBN10, Code39
from barcode.writer import ImageWriter, SVGWriter
from io import BytesIO

from django_tables2 import SingleTableView, LazyPaginator
from library.tables import BookTable, UserBookTable, UserTable
import pandas as pd
import zipfile
import time
import csv
import glob, os


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

def barcode_helper(m_number: str):
    rv = BytesIO()

    if len(m_number) == 13:
        try:
            ISBN13(str(m_number), writer=ImageWriter()).write(rv)
        except Exception:
            Code39(str(m_number), writer=ImageWriter(), add_checksum=False).write(rv)
    elif len(m_number) == 10:
        try:
            ISBN13(str(m_number), writer=ImageWriter()).write(rv)
        except Exception:
            Code39(str(m_number), writer=ImageWriter(), add_checksum=False).write(rv)
    else:
        Code39(str(m_number), writer=ImageWriter(), add_checksum=False).write(rv)

    return rv

def update_isbn_image(mBook: Book):
    mIsbn = mBook.isbn

    rv = barcode_helper(mIsbn)
    mBook.isbn_image.save(f"{mIsbn}.png", File(rv))

def update_user_barcode_image(mUser: User):
    userId = mUser.card_id
    rv = barcode_helper(userId)
    mUser.card_id_image.save(f"{userId}.png", File(rv))

def home(request):
    checkInForm = CheckInForm()
    checkOutForm = CheckOutForm()
    return render(request, "library/home.html", {"checkInForm": checkInForm,
                                                 "checkOutForm": checkOutForm})
def checkinout_only(request):
    checkInForm = CheckInForm()
    checkOutForm = CheckOutForm()
    return render(request, "library/checkinout-only.html", {"checkInForm": checkInForm,
                                                 "checkOutForm": checkOutForm})
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

    return render(request, 'library/user-details.html',{
        'user_name_form': user_name_form,
        'user_isbns_formset': user_isbns_formset,
        'user_details_form': user_details_form,
    })



    # if len(User.objects.filter(card_id=card_id)) > 0:
    #     mUser = User.objects.filter(card_id=card_id)[0]
    #     if request.method == "POST":
    #         detailsUserForm = UserDetailsForm(request.POST, instance=mUser)
    #         update_values = True
    #         if detailsUserForm.is_valid():
    #             for mIsbn in detailsUserForm.cleaned_data['isbns']:
    #                 print(f"mIsbn: {mIsbn}")
    #                 if len(Book.objects.filter(isbn=mIsbn)) == 0 and mIsbn != "":
    #                     update_values = False
    #                     print("found invalid isbn, do not update")
    #         else:
    #             update_values = False
    #         if update_values:
    #             detailsUserForm.save()
    #             mUser = User.objects.filter(card_id=detailsUserForm.cleaned_data["card_id"])[0]
    #             update_user_barcode_image(mUser)
    #             print("updated form!")
    #             messages.info(request, "Updated info for card {}".format(detailsUserForm.cleaned_data["card_id"]))
    #             return redirect("userDetails", card_id=detailsUserForm.cleaned_data["card_id"])
    #         else:
    #             messages.info(request, "Invalid form details, did not update card {}".format(card_id))
    #             mUser = User.objects.filter(card_id=card_id)[0]
    #             detailsUserForm = UserDetailsForm(instance=mUser)
    #     else:
    #         mUser = User.objects.filter(card_id=card_id)[0]
    #         print(f"get, returning form for {card_id}")
    #
    #     detailsUserForm = UserDetailsForm(instance=mUser)
    # else:
    #     detailsUserForm = UserDetailsForm()
    # return render(request, "library/user-details.html", {"form": detailsUserForm})

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
    return render(request, "library/new-user.html", {"form": newUserForm })

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
    return render(request, "library/remove-user.html", {"form": removeUserForm })

# def all_users(request):
#     users_list = []
#     for mUser in User.objects:
#         books_list = []
#
#         for mIsbn in mUser.isbns:
#             if len(Book.objects.filter(isbn=mIsbn)) > 0:
#                 print(f"this is > 0: {Book.objects.filter(isbn=mIsbn)}")
#                 mBook = Book.objects.filter(isbn=mIsbn)[0]
#                 books_list.append(mBook)
#             else:
#                 mUser.isbns.remove(mIsbn)
#                 mUser.save()



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

                return render(request, "library/user-books.html", {"form": userBooksForm,
                                                                  "table": mTable })
            else:
                messages.info(request, f"No user found for ID {userBooksForm.cleaned_data['card_id']}")
        else:
            print("form is invalid")


    return render(request, "library/user-books.html", {"form": ViewUserBooksForm()})

# def library(request):
#     return render(request, "library/library.html")

def new_book(request):

    manual_book_info_form = ManualAddBookForm()
    manual_book_title_form = BookDetailsTitleForm()
    author_formset = AuthorFormSet(prefix='authors')
    tag_formset = TagFormSet(prefix='tags')

    return render(request, "library/new-book.html", {
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
                update_isbn_image(mBook)
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
                        # mBook.tags.create(name=tag_form.cleaned_data['name'])
                mBook.tags = tag_list

                mBook.save()
                messages.info(request, "Added {} to your library".format(title_form.cleaned_data["title"]))


        # bookForm = ManualAddBookForm(request.POST)
        # if bookForm.is_valid():
        #     print(bookForm.cleaned_data["title"])
        #     existingBookList = Book.objects.filter(isbn=bookForm.cleaned_data["isbn"])
        #     if len(existingBookList) > 0:
        #         mBook = existingBookList[0]
        #         mBook.quantity += 1
        #         messages.info(request, "You now have {} copies of {}".format(mBook.quantity, mBook.title))
        #         mBook.save()
        #     else:
        #         bookForm.save()
        #         mBook = Book.objects.filter(isbn=bookForm.cleaned_data["isbn"])[0]
        #         update_isbn_image(mBook)
        #         messages.info(request, "Added {} to your library".format(bookForm.cleaned_data["title"]))

    return redirect("newBook",)

def new_book_isbn(request):
    if request.method == "POST":
        bookForm = ISBNAddBookForm(request.POST)
        if bookForm.is_valid():
            print(bookForm.cleaned_data["isbn"])
            bookDict = ISBNLookup().lookup(bookForm.cleaned_data["isbn"])
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
    return render(request, "library/remove-book.html", {"form": removeBookForm })

def book_details(request, isbn):
    print("book details")
    mBook = get_object_or_404(Book, isbn=isbn)

    if request.method == 'POST':
        book_info_form = BookDetailsContdForm(request.POST, instance=mBook)
        book_title_form = BookDetailsTitleForm(request.POST, instance=mBook)
        author_formset = AuthorFormSet(request.POST, prefix='authors')
        tag_formset = TagFormSet(request.POST, prefix='tags')

        # print(request.POST)

        print(f"book_info_form.is_valid()? {book_info_form.is_valid()}")
        print(f"book_title_form.is_valid()? {book_title_form.is_valid()}")
        print(f"author_formset.is_valid()? {author_formset.is_valid()}")
        print(f"tag_formset.is_valid()? {tag_formset.is_valid()}")

        print(f"author_formset.errors: {author_formset.errors}")
        print(f"book_info_form.errors: {book_info_form.errors}")

        if book_info_form.is_valid() and book_title_form.is_valid() and author_formset.is_valid() and tag_formset.is_valid():
            if isbn != book_info_form.cleaned_data["isbn"]:
                if len(Book.objects.filter(isbn=book_info_form.cleaned_data["isbn"])) == 0:

                    book_info_form.save()
                    update_isbn_image(mBook)

                else:
                    messages.info(request, f"Existing book with the ISBN {book_info_form.cleaned_data['isbn']}, not updating this book's ISBN")

            # Save authors and tags to the book instance
            mBook.authors.clear()
            # print(author_formset)
            # print("test")
            # print(type(author_formset))
            print("going to update author list")
            new_author_list = []
            for author_form in author_formset:
                if author_form.cleaned_data and author_form.cleaned_data['name'] != "":
                    new_author_list.append(author_form.cleaned_data['name'])
                    print(author_form.cleaned_data['name'])
                    # mBook.authors.create(name=author_form.cleaned_data['name'])
            mBook.authors = new_author_list

            mBook.tags.clear()
            new_tag_list = []
            # print(f"tag_formset: {tag_formset}")
            for tag_form in tag_formset:
                if tag_form.cleaned_data and tag_form.cleaned_data['name'] != "":
                    new_tag_list.append(tag_form.cleaned_data['name'])
                    # mBook.tags.create(name=tag_form.cleaned_data['name'])
            mBook.tags = new_tag_list

            mBook.save()
            messages.info(request, f"Updated {mBook.title}")

            return redirect('bookDetails', isbn=book_info_form.cleaned_data['isbn'])
        else:
            messages.info(request, f"Error updating {mBook.title}, invalid information")


            # return HttpResponseRedirect('/success/')
    # else:
    mBook = get_object_or_404(Book, isbn=isbn)
    book_info_form = BookDetailsContdForm(instance=mBook)
    book_title_form = BookDetailsTitleForm(instance=mBook)

    initial_authors = [{'name': author} for author in mBook.authors]
    author_formset = AuthorFormSet(prefix='authors', initial=initial_authors)
    initial_tags = [{'name': tag} for tag in mBook.tags]
    tag_formset = TagFormSet(prefix='tags', initial=initial_tags)

    # for author in mBook.authors:
    #     author_formset.add_fields(BookDetailsAuthorForm(initial={'name', author}), 0)
    #     print(author)

    # for f in author_formset:
    #     print(f)



    return render(request, 'library/book-details.html', {
        'book_info_form': book_info_form,
        'book_title_form': book_title_form,
        'author_formset': author_formset,
        'tag_formset': tag_formset,
    })


    # if len(Book.objects.filter(isbn=isbn)) > 0:
    #     mBook = Book.objects.filter(isbn=isbn)[0]
    #
    #     if request.method == "POST":
    #         detailsBookForm = BookDetailsForm(request.POST, instance=mBook)
    #         if detailsBookForm.is_valid():
    #             print(f"updated {detailsBookForm.cleaned_data['title']}")
    #             detailsBookForm.save()
    #             mBook = Book.objects.filter(isbn=detailsBookForm.cleaned_data['isbn'])[0]
    #             update_isbn_image(mBook)
    #             messages.info(request, "Updated info for {}".format(detailsBookForm.cleaned_data["title"]))
    #             return redirect('bookDetails', isbn=detailsBookForm.cleaned_data["isbn"])
    #         else:
    #             messages.info(request, "Invalid data for {}, did not update".format(detailsBookForm.cleaned_data["title"]))
    #     mBook = Book.objects.filter(isbn=isbn)[0]
    #     detailsBookForm = BookDetailsForm(instance=mBook)
    # else:
    #     detailsBookForm = BookDetailsForm()
    #
    # return render(request, "library/book-details.html", {"form": detailsBookForm})

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
        return redirect("checkinoutOnly")
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
        return redirect("checkinoutOnly")
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
            return render(request, "library/catalog.html", {"form": form,
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

    return render(request, "library/catalog.html", {"form": SearchForm(),
                                                    "table":BookTable(Book.objects.all().order_by(ordered_by)),
                                                    "num_results": num_results})

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

            # temp_df = pd.DataFrame.from_dict({"name": [mUser.name], "card_id": [mUser.card_id], "title": [mBook.title]})
            # print(temp_df)
            # user_df = pd.concat([user_df, temp_df])

    with open("all_users.csv", "w", newline="") as f:
        dict_writer = csv.DictWriter(f, user_keys)
        dict_writer.writeheader()
        dict_writer.writerows(user_list)

    return book_list, user_list

def books_report(request):
    book_list, user_list = report_helper()

    # return HttpResponse(book_list, content_type="application/csv")
    return FileResponse(open("all_books.csv", "rb"), as_attachment=False)
    # return render(str(book_df))

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

                    # print(s_line[4])
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

                    bookDict = ISBNLookup().lookup(isbn)
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
                    # messages.info(request, "Added {} to your library".format(bookDict["title"]))
                    book.quantity = quantity
                    book.save()

                # return redirect(request, "library/import-csv")
        else:
            messages.info(request, "Invalid form")

    return render(request, "library/import-csv.html", {"form": UploadFileForm()})

def tools(request):
    return render(request, "library/tools.html",)

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

def regenerate_barcodes_helper():
    book_files = glob.glob('book_isbn_images/*')
    card_files = glob.glob('card_id_images/*')
    for f in book_files:
        os.remove(f)
    for f in card_files:
        os.remove(f)

    for mBook in Book.objects.all():
        update_isbn_image(mBook)

    for mUser in User.objects.all():
        update_isbn_image(mUser)

    print("regenerated barcodes for all objects")

def generate_barcodes(request):
    regenerate_barcodes_helper()

    messages.info(request, "Generated ISBN and library card barcodes for objects in the database")

    return redirect("tools")

def book_isbn(request, filename):
    try:
        with open(f"book_isbn_images/{filename}", "rb") as f:
            return HttpResponse(f.read(), content_type="image/png")
    except FileNotFoundError:
        isbn = filename.split(".")[0]
        print(f"didn't find image, going to generate a new one for isbn {isbn}")
        if len(Book.objects.filter(isbn=isbn)) > 0:
            mBook = Book.objects.filter(isbn=isbn)[0]
            update_isbn_image(mBook)

            with open(f"book_isbn_images/{filename}", "rb") as f:
                return HttpResponse(f.read(), content_type="image/png")


def user_card_image(request, filename):
    try:
        with open(f"card_id_images/{filename}", "rb") as f:
            return HttpResponse(f.read(), content_type="image/png")
    except FileNotFoundError:
        card_id = filename.split(".")[0]
        print(f"didn't find image, going to generate a new one for card {card_id}")
        if len(User.objects.filter(card_id=card_id)) > 0:
            mUser = User.objects.filter(card_id=card_id)[0]
            update_user_barcode_image(mUser)
            with open(f"card_id_images/{filename}", "rb") as f:
                return HttpResponse(f.read(), content_type="image/png")