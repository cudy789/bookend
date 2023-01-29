from django.shortcuts import render, redirect
from isbnlookup.isbnlookup import ISBNLookup
from django.contrib import messages
from .forms import *
from django.http import FileResponse

from django_tables2 import SingleTableView
from library.tables import BookTable, UserBookTable
import pandas as pd
import zipfile


# Create your views here.
class MyTableClass(SingleTableView):
    table_class = BookTable
    queryset = Book.objects.all()
    template_name = "tables/catalog.html"

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
                messages.info(request, "Added {} to your library".format(newUserForm.cleaned_data["name"]))
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

def library(request):
    return render(request, "library/library.html")

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
                        mBook.quantity += 1
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
                        desiredBookList[0].quantity -= 1
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