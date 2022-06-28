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


    #def existfile(self, nfile, ext):
    #    """Генерация имени фала, если совпадает с существующим"""
    #    num = 0
    #    newfile = nfile + ext
    #    while os.path.exists(newfile):
    #        num += 1
    #        newfile = nfile + "_(%d)%s" % (num, ext)
    #    return newfile

    def tryAddCrc(self, filename):
        """Проверка на присутствие хеша"""
        fcrc32 = Crc32().crc32File(filename)
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
        return self.filelist.newFileIfExist(filename[0:-len(extmask)], newext)

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

    def operWithBook(self, book):
        """
        Обработка книги
            Если такая книги уже есть, сравнивается какая более полная.
        Параметры
        ---------
        book : Book
            Класс книги
        Возвращает
        ----------
        bool
            True - книга обработана
            False - книга удалена
        """
        if (book.is_dead()):
            return False
        book.showBook()
        if (ind := self.crc32list(book.Crc32())) > -1:
            # Совпала контрольная сумма с одной из ранее обработанных книг
            for prevBook in self.filesWithCrc32[ind]: # Просмотрим все книги
                if book.compareWith(prevBook) == 0:
                    book.is_dead = True
                    return False
        return True


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
            shortName = dfile.get("clearFileName") + dfile.get("extension")
            crc = Crc32().crc32File(filename)
            book = Book_Fb2(dfile.get("directory"), filename)
            if book.is_dead():
                del book
                book = None
            if shortName in files:
                ind = files.index(shortName)
                if crc == crc32List[ind]:
                    # Если файлы одинаковые (CRC32) - удалить дубликат #---, у которого длиннее имя
                    print(colored("[ДУБЛИКАТ (имя)]", "red", attrs = ["bold"]), "Удаляю файл:", self.fileList.getFullPath(filename))
                    self.fileList.fileDelete(filename)
                    continue
                # Если файлы разные - проверить книги
                if book != None:
                    if books[ind] != None:
                        res = book.compareWith(books[ind])
                        if res == 0:
                            print(colored("[ДУБЛИКАТ (книга)]", "red", attrs = ["bold"]), "Удаляю файл:", self.fileList.getFullPath(filename))
                            self.fileList.fileDelete(filename)
                            continue
                        if res == 10: # разные
                            files.append(shortName)
                            dfiles.append(dfile)
                            crc32List.append(crc)
                            books.append(book)
                            continue
                        if res < 0: # вторая полнее
                            print(colored("[Предыдущая версия (книга)]", "red", attrs = ["bold"]), "Удаляю файл:", self.fileList.getFullPath(filename))
                            self.fileList.fileDelete(filename)
                            continue
                        oldFile = dfiles[ind].get("fileName") + dfiles[ind].get("extension")
                        print(colored("[Предыдущая версия (книга)]", "red", attrs = ["bold"]), "Удаляю файл:", self.fileList.getFullPath(oldFile))
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
            if not (book := Book_Fb2(self.fileList.Directory(), filename)).is_dead():
                fileName = self.fileList.clearVersion(book.fileName()[0:-len(book.bookType())]) + book.bookType()
                book.showBook()
                if book.Crc32() in self.crc32list:
                    book.indexcrc32 = self.crc32list.index(book.Crc32())
                    #with bookItem in self.filesWithCrc32[ind]:
                    #    if (not book.is_dead()) and book.compareWith(bookItem) == 0:
                    #        self.files.fileDelete(book.fileName())
                    #        book.dead = True
                    #        print(colored("[ДУБЛИКАТ]", "red", attrs = ["bold"]), "Удалён файл: " + book.fullFileName())
                    #if book.is_dead():
                    #    del book
                    #else:
                    #    self.filesWithCrc32[ind].append(book)
                elif (not book.checkFileName()):
                    #book.indexcrc32 = ind
                    newfile = self.fileList.newFileIfExist(book.makeName(), book.bookType())
                    print(colored("[ОТЛАДКА]", "magenta", attrs = ["bold"]), "Новый файл:", newfile)
                    self.fileList.fileRename(book.fileName(), newfile)
                    book.renameFile(newfile)
                    self.fileList.setFileDateTime(book.fileName(), book.Born())

            else:
                del book
            print( "%d" % self.fileList.getPercent(), "%", end="\r")
            #print( "%d " % ((percent) * 100 // self.countfiles),"%", filename, self.countfiles)
            #self.checkFile(filename)
        print(colored("Проверка завершена", "green", attrs = ["bold"]))

Library = GoodBooks()
Library.start()
