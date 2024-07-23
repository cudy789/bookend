#!/usr/bin/python3

import urllib.request
import json

class ISBNLookup:
    """
    This class uses the Google Book API to populate relevant book information given a single ISBN number. The API
    doesn't always find a match for the ISBN, and sometimes the data it returns isn't completely filled out.
    """

    def __init__(self):
        pass

    def lookup(self, isbn_num:str):
        """
        Given an ISBN number (ISBN 10 or 13), return None if no book is found for a given ISBN, or returns
        a dictionary of the following structure:
            "title": m_title,
            "authors": m_authors,
            "subtitle": m_subtitle,
            "publisher": m_publisher,
            "publishedDate": m_publishedDate,
            "description": m_description,
            "isbn": isbn_num,
            "pageCount": m_pageCount,
            "categories": m_categories,
            "maturityRating": m_maturityRating,
            "averageRating": m_averageRating,
            "thumbnail": m_thumbnail,
            "publicDomain": m_publicDomain,
            "quantity": 1,
        :param isbn_num: a 10 or 13 numeric string to use for querying
        :return: None or a dict of the above structure.
        """

        base_api_link = "https://www.googleapis.com/books/v1/volumes?q=isbn:"

        print(base_api_link + isbn_num)

        with urllib.request.urlopen(base_api_link + isbn_num) as f: # our query to the google books api
            text = f.read()


        decoded_text = text.decode("utf-8")
        obj = json.loads(decoded_text) # deserializes decoded_text to a Python object

        if obj["totalItems"] == 0:
            print("No book found for that ISBN!")
            return None

        b_obj = obj["items"][0]

        try:
            m_title = b_obj["volumeInfo"]["title"]
        except KeyError as e:
            m_title = ""
        try:
            m_authors = b_obj["volumeInfo"]["authors"],
        except KeyError as e:
            m_authors = []
        try:
            m_subtitle = b_obj["volumeInfo"]["subtitle"],
        except KeyError as e:
            m_subtitle = ""
        try:
            m_publisher = b_obj["volumeInfo"]["publisher"]
        except KeyError as e:
            m_publisher = ""
        try:
            m_publishedDate = b_obj["volumeInfo"]["publishedDate"]
        except KeyError as e:
            m_publishedDate = ""
        try:
            m_description = b_obj["volumeInfo"]["description"]
        except KeyError as e:
            m_description = ""
        try:
            m_pageCount = b_obj["volumeInfo"]["pageCount"]
        except KeyError as e:
            m_pageCount = 0
        try:
            m_categories = b_obj["volumeInfo"]["categories"]
        except KeyError as e:
            m_categories = []
        try:
            m_maturityRating = b_obj["volumeInfo"]["maturityRating"]
        except KeyError as e:
            m_maturityRating = "NOT_MATURE"
        try:
            m_averageRating = b_obj["volumeInfo"]["averageRating"]
        except KeyError as e:
            m_averageRating = 0
        try:
            m_thumbnail = b_obj["volumeInfo"]["imageLinks"]["thumbnail"]
            if len(m_thumbnail) == 0:
                m_thumbnail = b_obj["volumeInfo"]["imageLinks"]["small_thumbnail"]
        except KeyError as e:
            m_thumbnail = ""
        try:
            m_publicDomain = b_obj["accessInfo"]["publicDomain"]
        except KeyError as e:
            m_publicDomain = "false"


        b_dict = {
            "title": m_title,
            "authors": m_authors,
            "subtitle": m_subtitle,
            "publisher": m_publisher,
            "publishedDate": m_publishedDate,
            "description": m_description,
            "isbn": isbn_num,
            "pageCount": m_pageCount,
            "categories": m_categories,
            "maturityRating": m_maturityRating,
            "averageRating": m_averageRating,
            "thumbnail": m_thumbnail,
            "publicDomain": m_publicDomain,
            "quantity": 1,
        }

        return b_dict

if __name__ == "__main__":
    print(ISBNLookup().lookup(input("enter isbn")))
