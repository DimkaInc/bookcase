#!/bin/python3

# -*- coding: utf-8 -*-
#import os, sys, shutil, zipfile, , zlib, pathlib, time
import datetime
from book import Book
from xml.dom import minidom

class Book_Fb2(Book):
    """Класс книги в формате FB2.
    Унаследован от класса Book"""

    lang = ""
    sequenceName = ""
    sequenceNumber = ""
    bookId = ""

    def fillFromDom(self, book):
        """
        Заполнение атрибутов книги
        Параметры
        ---------
        book : minidom Document
            Распарсенный XML документ
        """
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
        """
        Создаёт объекта книги
        Параметры
        ---------
        filename : str
            Имя фала с путём

        Возвращает
        ----------
        В случае неудачи, метод is_dead() вернёт True
        """
        super(Book_Fb2, self).__init__(filename)
        if self.booktype != ".fb2":
            self.dead = True
        else:
            book = minidom.parse(self.filename)
            self.fillFromDom(book)

    def Lang(self):
        """
        Язык книги
        Возвращает
        ----------
        str
            Язык книги (например: "ru", "en" и т.п.)
        """
        return self.lang # Язык книги

    def Sequence(self):
        """
        Серия, в которую входит книга
        Возвращает
        ----------
        str
            Серия вида: Название серии [том]
        """
        return "%s [%s]" % (self.sequenceName, self.sequenceNumber) # Серия книги

    def BookId(self):
        """
        Идентификатор книги (не ISBN и т.п.)
        Возвращает
        ----------
        str
            Идентификатор книги
        """
        return self.bookId # Идентификатор книги

    def ShowBook(self):
        """
        Выводит информацию о книге в консоль
        """
        print("ID:       %s" % self.BookId())
        print("Серия:    %s" % self.Sequence())
        super(Book_Fb2, self).ShowBook()

    def makeName(self):
        """
        Формирование имени книги для файла в формате: Серия-Автор-Название книги
        или Автор-Название книги, если нет серии
        Возвращает
        ----------
        str
            Название книги для файла
        """
        if (self.sequenceNumber != ""):
            return ("%s-%s" % (self.Sequence(), super(Book_Fb2, self).makeName())).replace(".", "").replace(" ", "_")
        return super(Book_Fb2, self).makeName()

    def compareWith(self, book):
        """
        Сравнение с другой книгой (book)
        Параметры
        ---------
        book : Book
            Вторая книги

        Возвращает
        ----------
        int
            Результат сравнения
            10 - книги разные
            -1 - одинаковые, вторая полнее
             0 - одинаковые, нет различий
             1 - одинаковые, эта полнее
        """
        if self.sequenceNumber != "":
            if self.Sequence() != book.Sequence():
                return 10
        return super(Book_Fb2, self).compareWith(book)
