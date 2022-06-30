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
from platform import python_version
from termcolor import colored
from colorama import init
from xml.dom import minidom
from book_fb2 import Book_Fb2
from crc32 import Crc32
from files import Files
import version

class GoodBooks:
    """Класс наведения порядка среди книг"""

    version = version.version
    author = "Дмитрий Добрышин"
    email = "dimkainc@mail.ru"

    crc32list = [] # хеши файлов
    filelist = None # имена файлов
    bookList = [] # список книг
    filesWithCrc32 = [] # список книг с crc32

    def __init__(self):

        # Инициализация Colorama
        sys.stdout.reconfigure(encoding = "utf-8")
        init(autoreset = True)
        now = datetime.datetime.now()
        #self.filelist = Files(".")
        print(colored("Приведение в порядок файлов книг", "green", attrs = ["bold"]),
          colored("(v" + self.version + ")", "red", attrs = ["bold"]))
        print(colored("©", "yellow", attrs = ["bold"]), 
          colored("%d" % now.year + " " + self.author, "white", attrs = ["bold"]),
          colored(self.email, "cyan", attrs = ["bold", "underline"]), "\n")


    def tryfb2epub(self, filename):
        newfile = self.tryNewFile(filename, ".fb2.epub", ".epub")
        if not newfile:
            return False
        os.rename(filename, newfile)
        print(colored("[EPUB]", "yellow", attrs = ["bold"]), "Файл переименован: " +
            newfile)
        return True

    def decodeZipFile(self, zipItem, zipFile=""):
        result = ""
        if zipItem.flag_bits & 0b1000:
            result = zipItem.filename.encode("cp437").decode("utf-8")
        elif ((zipItem.flag_bits & 0b100000000000) or (zipItem.flag_bits == 0)
            or (zipItem.flag_bits == 0b10)):
            result = zipItem.filename
        else:
            print(colored("[DEBUG] %s" % zipFile, "magenta", attrs = ["bold"]), "flags:", bin(zipItem.flag_bits) )
            try:
                result = zipItem.filename.encode("cp437").decode("cp866")
            except:
                result = zipItem.filename
        return result.replace("\\", os.path.sep)

    def extractFileFromZip(self, zipFile, zipItem):
        """
        Извлечение файла из архива в текущий каталог без сохранения структуры
        """

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

    def takeBook(self, dfile):
        """
        возвращает объект книги
        Параметры
        ---------
        dfile : dict
            Струкурированная запись о файле

        Возвращает
        ----------
        Book
            Объект книги или None
        """
        book = None
        if (ext := dfile.get("extension")) == ".fb2":
            book = Book_Fb2(dfile)
        elif ext == ".zip": # Извлечём все файлы из архива, а сам архив удалим
            arch = zipfile.ZipFile(os.path.join(dfile.get("directory"),
                dfile.get("fileName") + ext), "r")
            archItems = arch.infolist()
            print(colored("[ZIP]", "white", attrs = ["bold", "dark"]), "Распаковка файла: '%s%s'" % (dfile.get("fileName"), ext))
            for item in archItems:
                date_time = item.date_time
                ditem = self.fileList.getFileStruct(os.path.join(dfile.get("directory"),
                    self.decodeZipFile(item)))
                saveFile = os.path.join(ditem.get("directory"), self.fileList.newFileIfExist(
                    ditem.get("fileName"), ditem.get("extension")))
                source = arch.open(item)
                target = open(saveFile, "wb")
                with source, target:
                    shutil.copyfileobj(source, target)
                source.close()
                target.close()
                date_time = time.mktime(date_time + (0, 0, -1))
                os.utime(saveFile, (date_time, date_time))
                self.fileList.addFile(os.path.basename(saveFile))
        else:
            print(colored("[ОТЛАДКА]", "magenta", attrs = ["bold"]), "Не реализовано для типа файла: '%s'" % ext)
        if book != None and book.is_dead():
            del book
            book = None
        return book

    def start(self, directory = "."):
        percent = 0
        #self.files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
        self.fileList = Files(directory)
        files = []
        crc32List = []
        books = []
        dfiles = []
        print(colored("Производится учёт всех существующих файлов для исключения дубликатов", "white"))
        while( filename := self.fileList.getNextFile()):
            # Необходимо вычленить файлы, которые одинаково называются без версий
            dfile = self.fileList.getFileStruct(self.fileList.getFullPath(filename))
            if not dfile.get("extension") in [".fb2", ".zip", ".epub", ".fb2.zip", ".fb2.epub"]:
                continue
            shortName = dfile.get("clearFileName") + dfile.get("extension")
            crc = dfile.get("crc32")
            book = self.takeBook(dfile)
            #print(colored("[ОТЛАДКА]", "magenta", attrs = ["bold"]), "Краткое имя файла:", shortName)
            #print(colored("[ОТЛАДКА]", "magenta", attrs = ["bold"]), "CRC32:", crc)
            #print(colored("[ОТЛАДКА]", "magenta", attrs = ["bold"]), "Book:", book.is_dead())
            if book != None and book.is_dead():
                del book
                book = None
            if book != None:
                # переименование ниги, если отличается от реального
                newName = book.makeFileName()
                book.showBook()
                print(colored("[ОТЛАДКА]", "magenta", attrs = ["bold"]), "Старый файл:", book.fileName())
                print(colored("[ОТЛАДКА]", "magenta", attrs = ["bold"]), "Новый файл:", newName)
                if newName != shortName:
                    newFile = self.fileList.newFileIfExist(newName[0:-len(dfile.get("extension"))], dfile.get("extension"))
                    self.fileList.fileRename(book.fileName(), newFile)
                    book.filename = newFile
                    filename = newFile
                    dfile = self.fileList.getFileStruct(self.fileList.getFullPath(filename))
                    shortName = dfile.get("clearFileName") + dfile.get("extension")

            if shortName in files:
                ind = files.index(shortName)
                if crc == crc32List[ind]:
                    # Если файлы одинаковые (CRC32) - удалить дубликат #---, у которого длиннее имя
                    print(colored("[ДУБЛИКАТ]", "red", attrs = ["bold"]), "Удаляю файл:", self.fileList.getFullPath(filename))
                    self.fileList.fileDelete(filename)
                    continue
                # Если файлы разные - проверить книги
                if book != None:
                    if books[ind] != None:
                        res = book.compareWith(books[ind])
                        #print(colored("[ОТЛАДКА]", "magenta", attrs = ["bold"]), "Сравниваю:", book.bookName())
                        #print(colored("[ОТЛАДКА]", "magenta", attrs = ["bold"]), "и:", books[ind].bookName())
                        #print(colored("[ОТЛАДКА]", "magenta", attrs = ["bold"]), "Результат:", res)
                        if res == 0:
                            print(colored("[ДУБЛИКАТ]", "red", attrs = ["bold"]), "Удаляю файл:", self.fileList.getFullPath(filename))
                            self.fileList.fileDelete(filename)
                            continue
                        if res == 10: # разные
                            files.append(shortName)
                            dfiles.append(dfile)
                            crc32List.append(crc)
                            books.append(book)
                            continue
                        if res < 0: # вторая полнее
                            print(colored("[Предыдущая версия]", "red", attrs = ["bold"]), "Удаляю файл:", self.fileList.getFullPath(filename))
                            self.fileList.fileDelete(filename)
                            continue
                        oldFile = dfiles[ind].get("fileName") + dfiles[ind].get("extension")
                        print(colored("[Предыдущая версия]", "red", attrs = ["bold"]), "Удаляю файл:", self.fileList.getFullPath(oldFile))
                        self.fileList.fileDelete(oldFile)
                        print(colored("[ЗАМЕНА (книги)]", "yellow", attrs = ["bold"]), "Старый файл:", self.fileList.getFullPath(filename))
                        self.fileList.fileRename(filename, oldFile)
                        dfile.update({"fileName" : dfiles[ind].get("fileName")})
                        book.renameFile(oldFile)
                        dfiles[ind] = dfile
                        crc32List[ind] = crc
                        books[ind] = book
                        continue
                files.append(shortName)
                dfiles.append(dfile)
                crc32List.append(crc)
                books.append(book)
            else:
                if crc in crc32List:
                    #ind = crc32List.index(crc)
                    self.fileList.fileDelete(filename)
                    continue
                files.append(shortName)
                dfiles.append(dfile)
                crc32List.append(crc)
                books.append(book)
            # Если книги одинаковые, удалить ту, которая занимает меньше места и назначить самое короткое имя оставшейся
            # для книг .fb2.zip помнить информацию о самой книге, и сравнивать с книгами .fb2
            #if not (book := Book_Fb2(self.fileList.Directory(), filename)).is_dead():
            #    fileName = self.fileList.clearVersion(book.fileName()[0:-len(book.bookType())]) + book.bookType()
            #    book.showBook()
            #    if book.Crc32() in self.crc32list:
            #        book.indexcrc32 = self.crc32list.index(book.Crc32())
            #        #with bookItem in self.filesWithCrc32[ind]:
            #        #    if (not book.is_dead()) and book.compareWith(bookItem) == 0:
            #        #        self.files.fileDelete(book.fileName())
            #        #        book.dead = True
            #        #        print(colored("[ДУБЛИКАТ]", "red", attrs = ["bold"]), "Удалён файл: " + book.fullFileName())
            #        #if book.is_dead():
            #        #    del book
            #        #else:
            #        #    self.filesWithCrc32[ind].append(book)
            #    elif (not book.checkFileName()):
            #        #book.indexcrc32 = ind
            #        newfile = self.fileList.newFileIfExist(book.makeName(), book.bookType())
            #        print(colored("[ОТЛАДКА]", "magenta", attrs = ["bold"]), "Новый файл:", newfile)
            #        self.fileList.fileRename(book.fileName(), newfile)
            #        book.renameFile(newfile)
            #        self.fileList.setFileDateTime(book.fileName(), book.Born())

            #else:
            #    del book
            print( "%d" % self.fileList.getPercent(), "%", end="\r")
            #print( "%d " % ((percent) * 100 // self.countfiles),"%", filename, self.countfiles)
            #self.checkFile(filename)
        print(colored("Проверка завершена", "green", attrs = ["bold"]))

Library = GoodBooks()
Library.start()
