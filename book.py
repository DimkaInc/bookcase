#!/bin/python3

# -*- coding: utf-8 -*-
import os, datetime, pathlib, logging
from files import Files
from crc32 import Crc32

class Book:
    """Прототип класса книга."""
    chars2underline = [" ", ":", "|", "+", "<", ">", "\\", "/", "__", "☺"]
    chars2none = [".", ",", ";", "`", "«", "»", '"', "'", '’', "?", "*"]
    filename = "" # Имя файла
    directory = "" # Каталог размещения файла
    booktype = "" # Тип книги
    crc32 = ""    # Контрольная сумма
    bookname = "" # название книги
    author = "Неизвестен" # Автор
    born = 0.0    # Дата и время создания
    change = 0.0  # Дата и время изменения
    booksize = 0  # Размер книги
    dead = True
    logger = logging.getLogger("book")

    def is_dead(self):
        """
        Проверка уничтожения объекта
        Возвращает
        ----------
        bool
            Признак уничтожения объекта
        """
        return self.dead

    def __del__(self):
        self.dead = True

    def __init__(self, directory, filename):
        """
        Заполнение данных о книге из файла
        Параметры
        ---------
        directory : str
            Директория размещения файла
        filename : str
            Имя файла с путём
        """
        self.logger.info("Создан объект книга из каталога и имени файла")
        self.logger.debug("Каталог: %s, файл: %s" % (directory, filename))
        self.directory = directory
        self.filename = filename
        self.booktype = pathlib.Path(self.filename).suffix
        self.bookname = self.filename[0:-len(self.booktype)]
        stat = os.stat(self.filename)
        self.booksize = stat.st_size
        self.born = stat.st_atime
        self.change = stat.st_mtime
        self.crc32 = Crc32().crc32File(self.filename)
        self.dead = False

    def __init__(self, dfile):
        """
        Заполнение данных о книге из файла
        Параметры
        ---------
        dfile : dict
            структурированные данные о файле
        """
        self.logger.info("Создан объект книга из структурированной записи о файле")
        self.logger.debug("Запись: %s" % str(dfile))
        self.directory = dfile.get("directory")
        self.filename = dfile.get("fileName") + dfile.get("extension")
        self.booktype = dfile.get("extension")
        self.bookname = dfile.get("filename")
        stat = os.stat(os.path.join(self.directory, self.filename))
        self.booksize = stat.st_size
        self.born = stat.st_atime
        self.change = stat.st_mtime
        self.crc32 = dfile.get("crc32")
        self.dead = False

    def Directory(self):
        """
        Директория размещения файла
        Возвращает
        ----------
        str
            Директория
        """
        self.logger.debug("Directory()= %s" % self.directory)
        return self.directory

    def fileName(self):
        """
        Имя файла
        Возвращает
        ----------
        str
            Имя файла
        """
        self.logger.debug("fileName()= %s" % self.filename)
        return self.filename

    def fullFileName(self):
        """
        Полное имя файла с путём
        Возвращает
        ----------
        str
            Полное имя файла с путём
        """
        self.logger.debug("fullFileName()= %s" % os.path.join(self.directory, self.filename))
        return(os.path.join(self.directory, self.filename))

    def bookName(self):
        """
        Название книги
        Возвращает
        ----------
        str
            Название книги
        """
        self.logger.debug("bookName()= %s" % self.bookname)
        return self.bookname

    def Crc32(self):
        """
        Контрольная сумма CRC32
        Возвращает
        ----------
        int
            Контрольная сумма CRC32
        """
        self.logger.debug("Crc32()= %s" % self.crc32)
        return self.crc32

    def bookType(self):
        """
        Тип книги
        Возвращает
        ----------
        str
            Тип (расширение) книги
        """
        self.logger.debug("bookType()= %s" % self.booktype)
        return self.booktype

    def Author(self):
        """
        Автор книги
        Возвращает
        ----------
        str
            Автор
        """
        self.logger.debug("Author()= %s" % self.author)
        return self.author

    def bookSize(self):
        """
        Размер книги
        Возвращает
        ----------
        int
            Размер книги в байтах
        """
        self.logger.debug("bookSize()= %i" % self.booksize)
        return self.booksize

    def Born(self):
        """
        Дата и время создания книги
        Возвращает
        ----------
        datetime
            Дата и время создания книги
        """
        self.logger.debug("Born()= %s" % self.born)
        return self.born

    def Change(self):
        """
        Дата и время изменения книги
        Возвращает
        ----------
        datetime
            Дата и время изменения книги
        """
        self.logger.debug("Change()= %s" % self.change)
        return self.change

    def showBook(self):
        """
        Вывод данных о книге в консоль
        """
        self.logger.debug("Печать в консоль данных о книге")
        print("Название: %s" % self.bookName())
        print("Автор:    %s" % self.Author())
        print("Дата:     %s" % self.Born().strftime("%d.%m.%Y, %H:%M:%S"))
        #print("Каталог:  %s" % self.Directory())
        print("Файл:     %s" % self.fullFileName())
        print("Размер:   %d B" % self.bookSize())
        print("CRC32:    %s " % Crc32().hash2crc32(self.Crc32()))

    def replaces(self, source, fromList, toStr):
        """
        Замена набора строк на строку
        Параметры
        ---------
        source : str
            Исходная строка
        fromList : list of str
            Список строк, подлежащих замене
        toStr : str
            Строка, на кторую заменяются искомые строки

        Возвращает
        ----------
        str
            изменённая строка
        """
        self.logger.debug("replaces(%s, %s, %s)" % (source, str(fromList), toStr))
        for st in fromList:
            source = source.replace(st, toStr)
        self.logger.debug("replaces(...)= %s" % source)
        return source

    def makeName(self):
        """
        Формирование названия книги для файла в формате "Автор-Название_книги"
        Возвращает
        ----------
        str
            Название книги
        """
        name = self.replaces(self.bookName(), self.chars2underline, "_")
        name = self.replaces(name, self.chars2none, "")
        result = ("%s-%s" % (self.Author(), name)).replace("__", "_")
        self.logger.debug("makeName()= %s" % result)
        return result

    def makeFileName(self):
        """
        Формирование имени файла книги
        Возвращает
        ----------
        str
            Название книги с расширением
        """
        result = self.replaces("%s%s" % (self.makeName(), self.bookType()), self.chars2underline, "_")
        self.logger.debug("makeFileName()= %s", result)
        return result

    def renameFile(self, newFileName):
        """
        Переименовывает название файла книги
        Параметры
        ---------
        newFileName : str
            Новое название файла
        """
        self.logger.debug("renameFile(%s)" % newFileName)
        self.filename = newFileName

    def checkFileName(self):
        """
        Проверяет соответствие имени файла названию книги
        Возвращает
        ----------
        boolean
            True - файл соответствует названию
            False - файл не соответствует названию
        """
        self.logger.debug("checkFileName()= %s" % str(self.filename.find(self.makeName()) > -1))
        return self.filename.find(self.makeName()) > -1

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
        if self.Author() != book.Author():
            self.logger.debug("compareWith(%s)= 10" % str(book))
            return 10
        if self.bookName() != book.bookName():
            self.logger.debug("compareWith(%s)= 10" % str(book))
            return 10
        if self.Crc32() == book.Crc32():
            self.logger.debug("compareWith(%s)= 0" % str(book))
            return 0
        if self.bookSize() < book.bookSize():
            self.logger.debug("compareWith(%s)= -1" % str(book))
            return -1
        self.logger.debug("compareWith(%s)= 1" % str(book))
        return 1
