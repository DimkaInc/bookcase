#!/bin/python3

# -*- coding: utf-8 -*-
import datetime
from dateutil import parser # python3 -m pip install python-dateutil --upgrade
from book import Book
from xml.dom import minidom

class Book_Fb2(Book):
    """Класс книги в формате FB2.
    Унаследован от класса Book"""

    lang = ""
    sequenceName = ""
    sequenceNumber = ""
    bookId = ""

    def getItemTextFromXMLNode(self, xml_node, item):
        """
        Получение элемента из XML структуры
        Параметры
        ---------
        xml_node : object
            структурированный XML объект
        item : str
            требуемый элемент

        Возвращает
        ----------
        str
            Текстовое значение элемента или "" если ничего не найдено
        """
        #res = xml_node[0].getElementsByTagName(item)[0].childNodes[0].nodeValue
        try:
            res = xml_node[0].getElementsByTagName(item)[0].childNodes[0].nodeValue
        except:
            res = ""
        return res

    def fillFromDom(self, book):
        """
        Заполнение атрибутов книги
        Параметры
        ---------
        book : minidom Document
            Распарсенный XML документ
        """
        self.logger.debug("fillFromDom(%s)" % str(book))
        description = book.getElementsByTagName("description")
        titleinfo = description[0].getElementsByTagName("title-info")
        documentinfo = description[0].getElementsByTagName("document-info")
        publishinfo = description[0].getElementsByTagName("publish-info")
        self.lang = self.getItemTextFromXMLNode(titleinfo, "lang")
        #try:
        #    self.lang =   titleinfo[0].getElementsByTagName("lang"      )[0].childNodes[0].nodeValue
        #except:
        #    self.lang = ""

        authorFirst = self.getItemTextFromXMLNode(titleinfo, "first-name")
        if authorFirst == "":
            authorFirst = self.getItemTextFromXMLNode(documentinfo, "first-name")
        #try:
        #    authorFirst = titleinfo[0].getElementsByTagName("first-name")[0].childNodes[0].nodeValue
        #except:
        #    authorFirst = ""
        authorMiddle = self.getItemTextFromXMLNode(titleinfo, "middle-name")
        if authorMiddle == "":
            authorMiddle = self.getItemTextFromXMLNode(documentinfo, "middle-name")
        #try:
        #    authorMiddle = titleinfo[0].getElementsByTagName("middle-name")[0].childNodes[0].nodeValue
        #except:
        #    authorMiddle = ""
        if (ind := authorMiddle.find(" ")) > 0:
            authorMiddle = authorMiddle[0:ind]
        authorLast = self.getItemTextFromXMLNode(titleinfo, "last-name")
        if authorLast == "":
            authorLast = self.getItemTextFromXMLNode(documentinfo, "last-name")
        #try:
        #    authorLast = titleinfo[0].getElementsByTagName("last-name")[0].childNodes[0].nodeValue
        #except:
        #    authorLast = ""
        author = ("%s %s %s" % (authorFirst, authorMiddle, authorLast)).replace("  ", " ").strip()
        if author == "":
            self.author = "Неизвестен"
        else:
            self.author = self.replaces(author, self.chars2none, "")
        #print(str(titleinfo[0].getElementsByTagName("book-title")))
        #self.bookname = titleinfo[0].getElementsByTagName("book-title")[0].childNodes[0].nodeValue
        self.bookname = self.getItemTextFromXMLNode(titleinfo,"book-title")

        if self.bookname == "":
            self.bookname = self.getItemTextFromXMLNode(documentinfo,"book-title")
        if self.bookname == "":
            self.bookname = self.getItemTextFromXMLNode(publishinfo,"book-name")
        if self.bookname == "":
            self.bookname = "Неизвестное произведение"
        self.bookname = self.replaces(self.bookname, self.chars2none, "")
        #try:
        #    self.bookname = titleinfo[0].getElementsByTagName("book-title")[0].childNodes[0].nodeValue
        #except:
        #    self.bookname = "Неизвестное произведение"

        try:
            sequenceTag = titleinfo[0].getElementsByTagName("sequence")[0]
            self.sequenceName = sequenceTag.attributes['name'].value
            self.sequenceNumber = sequenceTag.attributes['number'].value
        except:
            self.sequenceName = ""
            self.sequenceNumber = ""

        #docinfo = description[0].getElementsByTagName("document-info")
        self.bookId = self.getItemTextFromXMLNode(documentinfo,"id")
        #try:
        #    self.bookId = docinfo[0].getElementsByTagName("id")[0].childNodes[0].nodeValue
        #except:
        #    self.bookId = ""

        try:
            bookDate = documentinfo[0].getElementsByTagName("date")[0].attributes["value"].value
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
        self.logger.info("Создание FB2 книги из каталога и файла")
        super(Book_Fb2, self).__init__(directory, filename)
        if self.booktype != ".fb2":
            self.logger.debug("Не FB2")
            self.dead = True
        else:
            #data = datetime.datetime.fromtimestamp(os.path.getctime(self.fullFileName()))
            try:
                book = minidom.parse(self.fullFileName())
            except:
                self.logger.error("Файл с повреждённой XML структурой")
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
        self.logger.info("Создание FB2 книги из структурированной записи о файле")
        super(Book_Fb2, self).__init__(dfile)
        if self.booktype != ".fb2":
            self.logger,debug("Не FB2")
            self.dead = True
        else:
            #data = datetime.datetime.fromtimestamp(os.path.getctime(self.fullFileName()))
            try:
                book = minidom.parse(self.fullFileName())
            except:
                self.logger.error("Файл с повреждённой XML структурой")
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
        self.logger.debug("Lang()= %s" % self.lang)
        return self.lang # Язык книги

    def Sequence(self):
        """
        Серия, в которую входит книга
        Возвращает
        ----------
        str
            Серия вида: Название серии [том]
        """
        result = ""
        if self.sequenceNumber != "":
            result = "%s [%s]" % (self.sequenceName, self.sequenceNumber) # Серия книги
        self.logger.debug("Sequence()= %s" % result)
        return result

    def BookId(self):
        """
        Идентификатор книги (не ISBN и т.п.)
        Возвращает
        ----------
        str
            Идентификатор книги
        """
        self.logger.debug("BookId()= %s" % self.bookId)
        return self.bookId # Идентификатор книги

    def showBook(self):
        """
        Выводит информацию о книге в консоль
        """
        self.logger.debug("Вывод информации о книге в консоль")
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
        result = super(Book_Fb2, self).makeName()
        if (self.sequenceNumber != ""):
            result = "%s-%s" % (self.Sequence(), result)
            result = self.replaces(result, self.chars2underline, "_")
            result = self.replaces(result, self.chars2none, "")
        self.logger.debug("makeName()= %s" % result)
        return result

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
                self.logger.debug("compareWith(%s)= 10" % str(book))
                return 10
        return super(Book_Fb2, self).compareWith(book)
