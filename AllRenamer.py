#!/bin/python3
'''
Приведение в порядок файлов книг

Обрабатывает файлы только из текущей директории.
[EPUB] - исправляет ошибочно названные *.fb2.epub в *.epub
[FB2.ZIP] - архивирует одинчноые файлы *.fb2, сохраняя признак книги, в *.fb2.zip

способ запуска:
   python AllRenamer.py
'''

# -*- coding: utf-8 -*-
import os, zipfile, datetime, zlib
from termcolor import colored
from colorama import init


class GoodBooks:
    """Класс наведения порядка среди книг"""

    version = "2.0.0.1"
    author = "Дмитрий Добрышин"
    email = "dimkainc@mail.ru"
    
    crc32list = [] # хеши файлов
    filelist = [] # имена файлов

    def __init__(self):
        
        # Инициализация Colorama
        init(autoreset = True)
        now = datetime.datetime.now()
        print(colored("Приведение в порядок файлов книг", "green", attrs = ["bold"]),
          colored("(v" + self.version + ")", "red", attrs = ["bold"]))
        print(colored("©", "yellow", attrs = ["bold"]), 
          colored("%d" % now.year + " " + self.author, "white", attrs = ["bold"]),
          colored(self.email, "cyan", attrs = ["bold", "underline"]), "\n")


    def crc32(self, filename, chunksize=65536):
        """Подсчёт CRC32 суммы для файла"""
        hash = 0
        with open(filename, "rb") as f:
            while (chunk := f.read(chunksize)):
                hash = zlib.crc32(chunk, hash)
        return "%08X" % (hash & 0xFFFFFFFF)

    def existfile(self, nfile, ext):
        """Генерация имени фала, если совпадает с существующим"""
        num = 0
        newfile = nfile + ext
        while os.path.exists(newfile):
            num += 1
            newfile = nfile + "_(%d)" % num + ext
        return newfile

    def tryAddCrc(self, filename):
        """Проверка на присутствие хеша"""
        fcrc32 = self.crc32(filename)
        if fcrc32 in self.crc32list:
            return False
        self.filelist.append(filename)
        self.crc32list.append(fcrc32)
        return True

    def tryNewFile(self, filename, extmask, newext):
        """
        Если файл имеет указанное окончание, 
        то возвращается новое свободное имя файла или False
        """
        if not filename.lower().endswith(extmask):
            return False
        return self.existfile(filename[0:-len(extmask)], newext)

    def tryfb2epub(self, filename):
        newfile = self.tryNewFile(filename, ".fb2.epub", ".epub")
        if not newfile:
            return False
        os.rename(filename, newfile)
        print(colored("[EPUB]", "yellow", attrs = ["bold"]), "Файл переименован: " +
            newfile)
        return True

    def tryfb2(self, filename):
        newfile = self.tryNewFile(filename, ".fb2", ".fb2.zip")
        #print(colored("DEBUG", "magenta", attrs = ["bold"]), newfile)
        if not newfile:
            return False
        archfile = zipfile.ZipFile(newfile, "w")
        archfile.write(filename, compress_type = zipfile.ZIP_DEFLATED)
        archfile.close()
        os.remove(filename)
        self.files.append(newfile)
        self.countfiles += 1
        print(colored("[FB2.ZIP]", "green", attrs = ["bold"]), "Файл сжат: " +
            newfile)
        return True

    def checkFile(self, filename):
        if self.tryAddCrc(filename):
            if self.tryfb2epub(filename):
                return True
            elif self.tryfb2(filename):
                return True
            return True
        os.remove(filename)
        print(colored("[ДУБЛИКАТ]", "red", attrs = ["bold"]), "Удалён файл: " + filename)
        return False

    def start(self, directory = "."):
        percent = 0
        self.files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
        self.countfiles = len(self.files)
        self.files.sort()
        print(colored("Производится учёт всех существующих файлов для исключения дубликатов", "white"))
        for filename in self.files:
            percent += 1
            print( "%d" % (percent * 100 // self.countfiles), "%", end="\r")
            self.checkFile(filename)
        print(colored("Проверка завершена", "green", attrs = ["bold"]))

Library = GoodBooks()
Library.start()
