#!/bin/python3

# -*- coding: utf-8 -*-
import os, datetime, pathlib
from files import Files
from crc32 import Crc32

class Book:
    """Прототип класса книга."""
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

    def Directory(self):
        """
        Директория размещения файла
        Возвращает
        ----------
        str
            Директория
        """
        return self.directory

    def fileName(self):
        """
        Имя файла
        Возвращает
        ----------
        str
            Имя файла
        """
        return self.filename

    def fullFileName(self):
        """
        Полное имя файла с путём
        Возвращает
        ----------
        str
            Полное имя файла с путём
        """
        return(os.path.join(self.directory, self.filename))

    def bookName(self):
        """
        Название книги
        Возвращает
        ----------
        str
            Название книги
        """
        return self.bookname

    def Crc32(self):
        """
        Контрольная сумма CRC32
        Возвращает
        ----------
        int
            Контрольная сумма CRC32
        """
        return self.crc32

    def bookType(self):
        """
        Тип книги
        Возвращает
        ----------
        str
            Тип (расширение) книги
        """
        return self.booktype

    def Author(self):
        """
        Автор книги
        Возвращает
        ----------
        str
            Автор
        """
        return self.author # Автор

    def bookSize(self):
        """
        Размер книги
        Возвращает
        ----------
        int
            Размер книги в байтах
        """
        return self.booksize

    def Born(self):
        """
        Дата и время создания книги
        Возвращает
        ----------
        datetime
            Дата и время создания книги
        """
        return self.born

    def Change(self):
        """
        Дата и время изменения книги
        Возвращает
        ----------
        datetime
            Дата и время изменения книги
        """
        return self.change

    def showBook(self):
        """
        Вывод данных о книге в консоль
        """
        print("Название: %s" % self.bookName())
        print("Автор:    %s" % self.Author())
        print("Дата:     %s" % self.Born().strftime("%d.%m.%Y, %H:%M:%S"))
        #print("Каталог:  %s" % self.Directory())
        print("Файл:     %s" % self.fullFileName())
        print("Размер:   %d B" % self.bookSize())
        print("CRC32:    %s " % Crc32().hash2crc32(self.Crc32()))

    def makeName(self):
        """
        Формирование названия книги для файла в формате "Автор-Название_книги"
        Возвращает
        ----------
        str
            Название книги
        """
        return ("%s-%s" % (self.Author(), self.bookName())).replace(" ", "_").replace(".", "")

    def makeFileName(self):
        """
        Формирование имени файла книги
        Возвращает
        ----------
        str
            Название книги с расширением
        """
        return ("%s%s" % (self.makeName(), self.bookType())).replace(" ", "_")

    def renameFile(self, newFileName):
        """
        Переименовывает название файла книги
        Параметры
        ---------
        newFileName : str
            Новое название файла
        """
        #os.rename(self.filename, newFileName)
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
            return 10
        if self.bookName() != book.bookName():
            return 10
        if self.Crc32() == book.Crc32():
            return 0
        if self.bookSize() < book.bookSize():
            return -1
        return 1
