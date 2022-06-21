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
import os, sys, shutil, zipfile, datetime, zlib, pathlib, time
from termcolor import colored
from colorama import init
from xml.dom import minidom
import version

class Crc32:
    """Подсчёт CRC32 суммы для файла"""

    def crc32(self, filename, chunksize=65536):

        hash = 0
        with open(filename, "rb") as f:
            while (chunk := f.read(chunksize)):
                hash = zlib.crc32(chunk, hash)
        return "%08X" % (hash & 0xFFFFFFFF)

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
    def makeFileName(self):
        return ("%s-%s%s" % (self.Author(), self.bookName(), self.bookType())).replace(" ", "_")

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

class Book_Fb2(Book):

    lang = ""
    sequenceName = ""
    sequenceNumber = ""
    bookId = ""

    def __init__(self, filename):
        super(Book_Fb2, self).__init__(filename)
        if self.booktype != ".fb2":
            self.dead = True
        else:
            book = minidom.parse(self.filename)
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

    def makeFileName(self):
        if (self.sequenceNumber != ""):
            return ("%s-%s-%s%s" % (self.Sequence(), self.Author(), self.bookName(), self.bookType())).replace(" ", "_")
        else:
            return super(Book_Fb2, self).makeFileName()

    def compareWith(self, book):
        if self.sequenceNumber != "":
            if self.Sequence() != book.Sequence():
                return 10
        return super(Book_Fb2, self).compareWith(book)

class GoodBooks:
    """Класс наведения порядка среди книг"""

    version = version.version
    author = "Дмитрий Добрышин"
    email = "dimkainc@mail.ru"
    
    crc32list = [] # хеши файлов
    filelist = [] # имена файлов

    def __init__(self):
        
        # Инициализация Colorama
        sys.stdout.reconfigure(encoding = "utf-8")
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
            newfile = nfile + "_(%d)%s" % (num, ext)
        return newfile

    def tryAddCrc(self, filename):
        """Проверка на присутствие хеша"""
        fcrc32 = self.crc32(filename)
        if fcrc32 in self.crc32list:
            return False
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
        self.appendFile(newfile)
        print(colored("[FB2.ZIP]", "green", attrs = ["bold"]), "Файл сжат: " +
            newfile)
        return True

    def appendFile(self, filename):
        self.files.append(filename)
        self.countfiles += 1

    def decodeZipFile(self, zipItem, zipFile=""):
        result = ""
        if zipItem.flag_bits & 0b1000:
            result = zipItem.filename.encode("cp437").decode("utf-8")
        elif (zipItem.flag_bits & 0b100000000000) or (zipItem.flag_bits == 0):
            result = zipItem.filename
        else:
            print(colored("[DEBUG] %s" % zipFile, "magenta", attrs = ["bold"]), "flags:", bin(zipItem.flag_bits) )
            try:
                result = zipItem.filename.encode("cp437").decode("cp866")
            except:
                result = zipItem.filename
        return result.replace("\\", os.path.sep)

    def extractFileFromZip(self, zipFile, zipItem):
        """Извлечение файла из архива в текущий каталог без сохранения структуры"""

        arch = zipfile.ZipFile(zipFile, "r")
        name, date_time = zipItem.filename, zipItem.date_time
        filename = os.path.basename(self.decodeZipFile(zipItem, zipFile))
        # проверка уникальности имени на всякий случай
        ext = pathlib.Path(filename.lower()).suffix
        filename = self.existfile(filename[0:-len(ext)], ext)
        
        source = arch.open(zipItem)
        target = open(filename, "wb")
        with source, target:
            shutil.copyfileobj(source, target)
        
        date_time = time.mktime(date_time + (0, 0, -1))
        os.utime(filename, (date_time, date_time))
        
        return filename

    def tryZip(self, filename):
        if not self.tryNewFile(filename, ".zip", ".rzip"):
            return False
        archfile = zipfile.ZipFile(filename, "r")
        includes = archfile.infolist()
        archfile.close()
        if len(includes) > 1:
          for item in includes:
            ext = pathlib.Path(item.filename.lower()).suffix
            if ext in [".zip", ".epub", ".fb2", ".rtf", ".pdf", ".docx", ".doc", ".txt"]:
                unicodename = self.extractFileFromZip(filename, item)
                self.appendFile(unicodename)
                print(">>> %s" % unicodename)
        else:
            if (not filename.lower().endswith(".fb2.zip") and
                includes[0].filename.lower().endswith(".fb2")):
                if (newfile := self.tryNewFile(filename, ".zip", ".fb2.zip")):
                    os.rename(filename, newfile)
            
        archfile.close()


    def checkFile(self, filename):
        if self.tryAddCrc(filename):
            if self.tryfb2epub(filename):
                return True
            elif self.tryfb2(filename):
                return True
            elif self.tryZip(filename):
                return True
            return True
        try:
            os.remove(filename)
            print(colored("[ДУБЛИКАТ]", "red", attrs = ["bold"]), "Удалён файл: " + filename)
        except OSError as e:
            print("Failed with:", e.strerror) # look what it says
            print("Error code:", e.code)
        return False

    def start(self, directory = "."):
        percent = 0
        self.files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
        self.countfiles = len(self.files)
        self.files.sort()
        print(colored("Производится учёт всех существующих файлов для исключения дубликатов", "white"))
        for filename in self.files:
            percent += 1
            if not (book := Book_Fb2(filename)).is_dead():
                book.ShowBook()
                print(book.makeFileName())
            else:
                del book
            print( "%d" % ((percent) * 100 // self.countfiles), "%", end="\r")
            #print( "%d " % ((percent) * 100 // self.countfiles),"%", filename, self.countfiles)
            self.checkFile(filename)
        print(colored("Проверка завершена", "green", attrs = ["bold"]))

Library = GoodBooks()
Library.start()
