#!/bin/python3

# -*- coding: utf-8 -*-
#import os, sys, shutil, zipfile, time
import datetime, zlib, pathlib
from book_fb2 import Book_Fb2
from xml.dom import minidom

class Book_Fb2_Zip(Book_Fb2):

    lang = ""
    sequenceName = ""
    sequenceNumber = ""
    bookId = ""

    def fillFromDom(self, book):
        description = book.getElementsByTagName("description")
        titleinfo = description[0].getElementsByTagName("title-info")
        self.lang = titleinfo[0].getElementsByTagName("lang")[0].childNodes[0].nodeValue

        authorFirst = titleinfo[0].getElementsByTagName("first-name")[0].childNodes[0].nodeValue
        authorLast = titleinfo[0].getElementsByTagName("last-name")[0].childNodes[0].nodeValue
        self.author = "%s %s" % (authorFirst, authorLast)

        self.bookname = titleinfo[0].getElementsByTagName("book-title")[0].childNodes[0].nodeValue

        sequenceTag = titleinfo[0].getElementsByTagName("sequence")[0]
        self.sequenceName = sequenceTag.attributes['name'].value
        self.sequenceNumber = sequenceTag.attributes['number'].value

        docinfo = description[0].getElementsByTagName("document-info")
        self.bookId = docinfo[0].getElementsByTagName("id")[0].childNodes[0].nodeValue

        bookDate = docinfo[0].getElementsByTagName("date")[0].attributes["value"].value
        self.born = datetime.datetime.strptime(bookDate, "%Y-%m-%d %H:%M:%S")

    def __init__(self, filename):
        super(Book_Fb2, self).__init__(filename)
        suffixes = pathlib.Path(self.filename).suffixes)
        if (suffixes.lenght < 2):
            self.dead = True
        else:
            self.booktype = "".join(suffixes[-2], suffixes[-1])

        if self.booktype != ".fb2.zip":
            self.dead = True
        else:
            book = minidom.parseString(self.filename)
            self.fillFromDom(book)

    def Lang(self):
        return self.lang # Язык книги

    def Sequence(self):
        return "%s [%s]" % (self.sequenceName, self.sequenceNumber) # Серия книги

    def BookId(self):
        return self.bookId # Идентификатор книги

    def ShowBook(self):
        print("ID:       %s" % self.BookId())
        print("Серия:    %s" % self.Sequence())
        super(Book_Fb2, self).ShowBook()

    def makeName(self):
        if (self.sequenceNumber != ""):
            return ("%s-%s" % (self.Sequence(), super(Book_Fb2, self).makeName())).replace(".", "").replace(" ", "_")
        else:
            return super(Book_Fb2, self).makeName()

    def compareWith(self, book):
        if self.sequenceNumber != "":
            if self.Sequence() != book.Sequence():
                return 10
        return super(Book_Fb2, self).compareWith(book)
