from django.shortcuts import render, redirect
from isbnlookup.isbnlookup import ISBNLookup
from django.contrib import messages
from .forms import *
from django.http import FileResponse
from django.db.models import Sum

from django_tables2 import SingleTableView, LazyPaginator
from library.tables import BookTable, UserBookTable, UserTable
import pandas as pd
import zipfile
import time


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

def home(request):
    checkInForm = CheckInForm()
    checkOutForm = CheckOutForm()
    return render(request, "library/home.html", {"checkInForm": checkInForm,
                                                 "checkOutForm": checkOutForm})

def new_user(request):
    if request.method == "POST":
        newUserForm = NewUserForm(request.POST)
        if newUserForm.is_valid():
            existingUsers = User.objects.filter(card_id=newUserForm.cleaned_data["card_id"])
            if len(existingUsers) > 0:
                messages.info(request, "User with Id: {} already exists".format(newUserForm.cleaned_data["card_id"]))
            else:
                newUserForm.save()
                messages.info(request, "{}'s profile has been created".format(newUserForm.cleaned_data["name"]))
    newUserForm = NewUserForm()
    return render(request, "library/new-user.html", {"form": newUserForm })

def user_books(request):
    if request.method == "POST":
        userBooksForm = ViewUserBooksForm(request.POST)
        if userBooksForm.is_valid():
            existingUsers = User.objects.filter(card_id=userBooksForm.cleaned_data["card_id"])
            if len(existingUsers) > 0:
                mUser = existingUsers[0]
                mBookList = []
                for misbn in mUser.isbns:
                    mBook = Book.objects.filter(isbn=misbn)[0]
                    mBookList.append(mBook)

                mTable = UserBookTable(mBookList)

                return render(request, "library/user-books.html", {"form": userBooksForm,
                                                                  "table": mTable })
            else:
                messages.info(request, "User does not exist")
        else:
            print("form is invalid")


    return render(request, "library/user-books.html", {"form": ViewUserBooksForm()})

# def library(request):
#     return render(request, "library/library.html")

def new_book(request):
    return render(request, "library/new-book.html", {"ISBNForm": ISBNAddBookForm(), "manualForm": ManualAddBookForm()})

def new_book_manual(request):
    if request.method == "POST":
        bookForm = ManualAddBookForm(request.POST)
        if bookForm.is_valid():
            print(bookForm.cleaned_data["title"])
            existingBookList = Book.objects.filter(title=bookForm.cleaned_data["title"])
            if len(existingBookList) > 0:
                mBook = existingBookList[0]
                mBook.quantity += 1
                messages.info(request, "You now have {} copies of {}".format(mBook.quantity, mBook.title))
                mBook.save()
            else:
                bookForm.save()
                messages.info(request, "Added {} to your library".format(bookForm.cleaned_data["title"]))

    return redirect("newBook",)

def new_book_isbn(request):
    if request.method == "POST":
        bookForm = ISBNAddBookForm(request.POST)
        if bookForm.is_valid():
            print(bookForm.cleaned_data["isbn"])
            bookDict = ISBNLookup().lookup(bookForm.cleaned_data["isbn"])

            if bookDict is None:
                messages.info(request, "Error, could not add book")
            else:
                book = Book.objects.filter(isbn=bookForm.cleaned_data["isbn"])
                if len(book) == 0:
                    book = Book(**bookDict)
                    messages.info(request, "Added {} to your library".format(bookDict["title"]))
                    book.quantity = 1
                    book.save()
                else:
                    book[0].quantity += 1
                    book[0].save()
                    messages.info(request, "You now have {} copies of {}".format(book[0].quantity, book[0].title))



    return redirect("newBook", )

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
                    messages.info(request, "Invalid card id")
                    print("invalid card id")
            else:
                messages.info(request, "Book with entered ISBN is not in your library")
                print("book with entered ISBN is not in your library")
        else:
            print("form is invalid")
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
                        messages.info(request, "Checkout {} to {}".format(desiredBookList[0].title, userList[0].name))
                        print("Checkout {} to {}".format(desiredBookList[0].title, userList[0].name))
                    else:
                        messages.info(request, "Invalid card id")
                        print("invalid card id")
                else:
                    messages.info(request, "All copies of {} are already checked out".format(desiredBookList[0].title))
            else:
                messages.info(request, "Book with entered ISBN is not in your library")
                print("book with entered ISBN is not in your library")
        else:
            print("form is invalid")
    print("redirecting to home")
    return redirect("home")

def catalog(request):
    form = SearchForm(request.POST)
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
                    | Book.objects.filter(categories__regex=query_regex)
                    | Book.objects.filter(isbn__regex=query_regex)
                    )
            print(f"results: {results}")
            if len(results) > 0:
                num_results = results.aggregate(Sum("quantity"))["quantity__sum"]
            else:
                num_results = 0
            return render(request, "library/catalog.html", {"form": form,
                                                           "table": BookTable(results),
                                                            "num_results": num_results
                                                            })
    if len(Book.objects.all()) > 0:
        num_results = Book.objects.all().aggregate(Sum("quantity"))["quantity__sum"]
    else:
        num_results = 0

    return render(request, "library/catalog.html", {"form": SearchForm(), "table":BookTable(Book.objects.all()),
                  "num_results": num_results})

def generate_report(request):
    book_df = pd.DataFrame()
    for mBook in Book.objects.all():
        book_df = pd.concat([book_df, pd.DataFrame.from_dict(mBook.__dict__)])

    user_df = pd.DataFrame()
    for mUser in User.objects.all():

        for index, misbn in enumerate(mUser.isbns):
            mBook = Book.objects.filter(isbn=misbn)[0]
            temp_df = pd.DataFrame.from_dict({"name": [mUser.name], "card_id": [mUser.card_id], "title": [mBook.title]})
            print(temp_df)
            user_df = pd.concat([user_df, temp_df])


    f_book_df = book_df.filter(items=["title", "authors", "publisher", "publishedDate", "quantity"])
    f_book_df.to_csv("all_books.csv")
    print(user_df)
    user_df.to_csv("users.csv")

    with zipfile.ZipFile("report.zip", mode="w") as archive:
        archive.write("all_books.csv")
        archive.write("users.csv")

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
                    s_line = line.split(",")
                    print(s_line[0])

                    print(s_line[4])
                    if not s_line[4].isnumeric() or int(s_line[4]) > 100:
                        quantity=1
                    else:
                        quantity = s_line[4]

                    isbn = s_line[3]
                    if not isbn.isnumeric():
                        m_dict = {"title": s_line[0],
                                  "authors": s_line[1:3],
                                  "quantity": quantity,
                                  }
                        Book(**m_dict).save()
                    else:
                        bookDict = ISBNLookup().lookup(isbn)
                        time.sleep(3)

                        if bookDict is None:
                            bookDict = {"title": s_line[0],
                                      "authors": s_line[1:3],
                                      "isbn": isbn,
                                      "quantity": quantity,
                                      }
                        else:
                            bookDict["title"] = s_line[0]
                            bookDict["authors"] = s_line[1:3]
                            bookDict["isbn"] = isbn
                            bookDict["quantity"] = quantity

                        book = Book.objects.filter(isbn=isbn)
                        if len(book) == 0:
                            book = Book(**bookDict)
                            # messages.info(request, "Added {} to your library".format(bookDict["title"]))
                            book.quantity = quantity
                            book.save()
                        else:
                            book[0].quantity = quantity
                            book[0].save()
                            # messages.info(request,"You now have {} copies of {}".format(book[0].quantity, book[0].title))




                # return redirect(request, "library/import-csv")
        else:
            messages.info(request, "Invalid form")

    return render(request, "library/import-csv.html", {"form": UploadFileForm()})

