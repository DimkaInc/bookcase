#!/bin/python3

# -*- coding: utf-8 -*-
import datetime
from dateutil import parser
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
        try:
            self.lang = titleinfo[0].getElementsByTagName("lang")[0].childNodes[0].nodeValue
        except:
            self.lang = ""

        try:
            authorFirst = titleinfo[0].getElementsByTagName("first-name")[0].childNodes[0].nodeValue
        except:
            authorFirst = ""
        try:
            authorMiddle = titleinfo[0].getElementsByTagName("middle-name")[0].childNodes[0].nodeValue
        except:
            authorMiddle = ""
        if (ind := authorMiddle.find(" ")) > 0:
            authorMiddle = authorMiddle[0:ind]
        try:
            authorLast = titleinfo[0].getElementsByTagName("last-name")[0].childNodes[0].nodeValue
        except:
            authorLast = ""
        author = ("%s %s %s" % (authorFirst, authorMiddle, authorLast)).replace("  ", " ").strip()
        if author == "":
            self.author = "Неизвестен"
        else:
            self.author = author

        self.bookname = titleinfo[0].getElementsByTagName("book-title")[0].childNodes[0].nodeValue
        try:
            sequenceTag = titleinfo[0].getElementsByTagName("sequence")[0]
            self.sequenceName = sequenceTag.attributes['name'].value
            self.sequenceNumber = sequenceTag.attributes['number'].value
        except:
            self.sequenceName = ""
            self.sequenceNumber = ""

        docinfo = description[0].getElementsByTagName("document-info")
        try:
            self.bookId = docinfo[0].getElementsByTagName("id")[0].childNodes[0].nodeValue
        except:
            self.bookId = ""

        try:
            bookDate = docinfo[0].getElementsByTagName("date")[0].attributes["value"].value
            self.born = parser.parse(bookDate)
        except:
            self.born = datetime.datetime.fromtimestamp(self.born)

    def __init__(self, directory, filename):
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
        super(Book_Fb2, self).__init__(directory, filename)
        if self.booktype != ".fb2":
            self.dead = True
        else:
            #data = datetime.datetime.fromtimestamp(os.path.getctime(self.fullFileName()))
            try:
                book = minidom.parse(self.fullFileName())
            except:
                self.dead = True
            if not self.is_dead():
                self.fillFromDom(book)

    def __init__(self, dfile):
        """
        Создаёт объекта книги
        Параметры
        ---------
        dfile : dict
            Структурированные данные о файле

        Возвращает
        ----------
        В случае неудачи, метод is_dead() вернёт True
        """
        super(Book_Fb2, self).__init__(dfile)
        if self.booktype != ".fb2":
            self.dead = True
        else:
            #data = datetime.datetime.fromtimestamp(os.path.getctime(self.fullFileName()))
            try:
                book = minidom.parse(self.fullFileName())
            except:
                self.dead = True
            if not self.is_dead():
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
        if self.sequenceNumber == "":
            return ""
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

    def showBook(self):
        """
        Выводит информацию о книге в консоль
        """
        print("ID:       %s" % self.BookId())
        print("Серия:    %s" % self.Sequence())
        super(Book_Fb2, self).showBook()

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
            return self.replaces("%s-%s" % (self.Sequence(), super(Book_Fb2, self).makeName()), self.chars2underline, "_")
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
