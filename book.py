#!/bin/python3

# -*- coding: utf-8 -*-
import os, datetime, pathlib
from crc32 import Crc32

class Book:
    """Прототип класса книга."""
    filename = ""
    booktype = ""
    crc32 = ""
    bookname = ""
    author = "Неизвестен"
    born = 0.0
    change = 0.0
    booksize = 0
    dead = True

    def is_dead(self):
        return self.dead

    def __del__(self):
        # none
        self.dead = True

    def __init__(self, filename):
        self.filename = filename.lower()
        self.booktype = pathlib.Path(self.filename).suffix
        self.bookname = self.filename[0:-len(self.booktype)]
        stat = os.stat(self.filename)
        self.booksize = stat.st_size
        self.born = stat.st_atime
        self.change = stat.st_mtime
        self.crc32 = Crc32().crc32(self.filename)
        self.dead = False


    def fileName(self):
        return self.filename # Имя файла

    def bookName(self):
        return self.bookname # Название книги

    def Crc32(self):
        return self.crc32 # Контрольная сумма книги

    def bookType(self):
        return self.booktype # Тип книги

    def Author(self):
        return self.author # Автор

    def bookSize(self):
        return self.booksize # Размер книги

    def Born(self):
        return self.born # Дата и время создания книги

    def Change(self):
        return self.change # Дата и время изменения книги

    def ShowBook(self):
        print("Название: %s" % self.bookName())
        print("Автор:    %s" % self.Author())
        print("Дата:     %s" % self.Born().strftime("%d.%m.%Y, %H:%M:%S"))
        print("Файл:     %s" % self.fileName())
        print("Размер:   %d B" % self.bookSize())

    def makeName(self):
        return ("%s-%s" % (self.Author(), self.bookName())).replace(" ", "_").replace(".", "")

    def makeFileName(self):
        return ("%s%s" % (self.makeName(), self.bookType())).replace(" ", "_")

    def renameFile(self, newFileName):
        os.rename(self.filename, newFileName)
        self.filename = newFileName

    def compareWith(self, book):
        """
        Сравнение с другой книгой (book)

          10 - разные
          -1 - одинаковые, другая полнее
          0  - одинаковые равные
          1  - одинаковые, эта полнее
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
