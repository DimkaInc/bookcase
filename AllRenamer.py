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
import os, sys, shutil, zipfile, datetime, zlib, pathlib, time, logging, logging.config
import yaml # pyyaml
#logging.basicConfig(
#    filename = sys.argv[0]+".log",
#    filemode = "w",
#    encoding = "utf-8",
#    format = "%(asctime)s %(filename)s-%(lineno)d-%(module)s-[%(levelname)s]:%(message)s",
#    datefmt = "%d.%m.%Y %H:%M:%S",
#    level = logging.DEBUG
#) # DEBUG INFO WARNING ERROR CRITICAL
with open("AllRenamer.yaml", "r") as stream:
    logging.config.dictConfig(yaml.safe_load(stream))

from platform import python_version
from sys import platform
from termcolor import colored
from colorama import init
from xml.dom import minidom
from book_fb2 import Book_Fb2
from crc32 import Crc32
from files import Files
import version
#from debug import *

class GoodBooks:
    """Класс наведения порядка среди книг"""

    version = version.version
    author = "Дмитрий Добрышин"
    email = "dimkainc@mail.ru"

    crc32list = [] # хеши файлов
    filelist = None # имена файлов
    bookList = [] # список книг
    filesWithCrc32 = [] # список книг с crc32
    logger = logging.getLogger("goodbook")

    def __init__(self):

        # Инициализация Colorama
        sys.stdout.reconfigure(encoding = "utf-8")
        init(autoreset = True)
        now = datetime.datetime.now()
        #self.filelist = Files(".")
        self.logger.info("Инициализирован класс")
        print(
            colored("Приведение в порядок файлов книг", "green", attrs = ["bold"]),
            colored("(v" + self.version + ")", "red", attrs = ["bold"])
        )
        print(
            colored("©", "yellow", attrs = ["bold"]),
            colored("%d" % now.year + " " + self.author, "white", attrs = ["bold"]),
            colored(self.email, "cyan", attrs = ["bold", "underline"]), "\n"
        )


    def tryfb2epub(self, filename):
        newfile = self.tryNewFile(filename, ".fb2.epub", ".epub")
        if not newfile:
            return False
        os.rename(filename, newfile)
        self.logger.info("Файл переименован: %s" % newfile)
        print(
            colored("[EPUB]", "yellow", attrs = ["bold"]),
            "Файл переименован: $s" % newfile
        )
        return True

    def decodeZipFile(self, zipItem, zipFile = ""):
        result = ""
        self.logger.debug("%s флаг: %s" % (zipFile, bin(zipItem.flag_bits)))

        if zipItem.flag_bits == 0:
            try:
                result = zipItem.filename.encode("cp437").decode("cp866")
            except Exception as e:
                print(
                    colored("[ОШИБКА] %s" % zipFile, "magenta", attrs = ["bold"]),
                    "код:", sys.exc_info()[0]
                )
                self.logger.error("код: %s" % sys.exc_info()[0])
                self.logger.debug("%s, флаги: %s файл: %s" % (zipFile, bin(zipItem.flag_bits), zipItem.filename))
                result = zipItem.filename
        elif zipItem.flag_bits == 0b10:
            self.logger.debug("%s, флаги: %s файл: %s" % (zipFile, bin(zipItem.flag_bits), zipItem.filename))
            result = zipItem.filename
        elif zipItem.flag_bits == 0b1000:
            try:
                result = zipItem.filename.encode("cp437").decode("utf-8")
            except:
                print(
                    colored("[ОШИБКА]", "magenta", attrs = ["bold"]),
                    "код:", sys.exc_info()[0]
                )
                self.logger.error("код: %s" % sys.exc_info()[0])
                self.logger.debug("%s, флаги: %s файл: %s" % (zipFile, bin(zipItem.flag_bits), zipItem.filename))
                result = zipItem.filename
        elif zipItem.flag_bits == 0b100000000000:
            self.logger.debug("%s, флаги: %s файл: %s" % (zipFile, bin(zipItem.flag_bits), zipItem.filename))
            result = zipItem.filename
        else:
            self.logger.debug("%s, флаги: %s файл: %s" % (zipFile, bin(zipItem.flag_bits), zipItem.filename))
            try:
                result = zipItem.filename.encode("cp437").decode("cp866")
            except:
                print(
                    colored("[ОШИБКА]", "magenta", attrs = ["bold"]),
                    "код:", sys.exc_info()[0]
                )
                self.logger.error("код: %s" % sys.exc_info()[0])
                self.logger.debug("%s, флаги: %s файл: %s" % (zipFile, bin(zipItem.flag_bits), zipItem.filename))
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
            print(
                colored("[ДУБЛИКАТ]", "red", attrs = ["bold"]),
                "Удалён файл: %s" % filename
            )
            self.logger.info("Удалён  файл: %s" % filename)
        except OSError as e:
            self.logger.error("Ошибка: %s, код %s" % (e.strerror, e.code))
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
            self.logger.info("[FB2] обработка книги \"%s%s\"" % (dfile.get("fileName"), ext))
            book = Book_Fb2(dfile)
        elif ext == ".zip": # Извлечём все файлы из архива, а сам архив удалим
            self.logger.info("[ZIP] Распаковка файла: \"%s%s\"" % (dfile.get("fileName"), ext))
            print(
                colored("[ZIP]", "white", attrs = ["bold", "dark"]),
                "Распаковка файла: '%s%s'" % (dfile.get("fileName"), ext)
            )
            try:
                arch = zipfile.ZipFile(os.path.join(dfile.get("directory"),
                    dfile.get("fileName") + ext), "r")
            except:
                self.logger.warning("Архив повреждён и удалён: %s" % dfile.get("fileName") + ext)
                self.fileList.fileDelete(dfile.get("fileName") + ext)
                return book
            archItems = arch.infolist()
            for item in archItems:
                if item.is_dir():
                    continue
                date_time = item.date_time
                ditem = self.fileList.getFileStruct(os.path.join(dfile.get("directory"),
                    self.decodeZipFile(item)))
                saveFile = os.path.join(dfile.get("directory"), self.fileList.newFileIfExist(
                    ditem.get("fileName"), ditem.get("extension")))
                self.logger.debug("%s файл: \"%s\"" % (dfile.get("fileName") + ext, saveFile))
                source = arch.open(item)
                target = open(saveFile, "wb")
                with source, target:
                    shutil.copyfileobj(source, target)
                source.close()
                target.close()
                date_time = time.mktime(date_time + (0, 0, -1))
                os.utime(saveFile, (date_time, date_time))
                self.fileList.addFile(os.path.basename(saveFile))
            arch.close()
            self.fileList.fileDelete(dfile.get("fileName") + ext)
            self.logger.info("[ZIP] Удалён распакованный файл: %s%s" % (dfile.get("fileName"), ext))
            print(
                colored("[ZIP]", "red", attrs = ["bold"]),
                "Удалён распакованный файла: '%s%s'" % (dfile.get("fileName"), ext)
            )
        else:
            self.logger.debug("Не реализовано для типа файла %s \"%s%s\""  % (ext, dfile.get("fileName"), ext))
            print(
                colored("[ОТЛАДКА]", "magenta", attrs = ["bold"]),
                "Не реализовано для типа файла: '%s'" % ext
            )
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
        self.logger.info("Запуск обработки")
        print(
            colored("Производится учёт всех существующих файлов для исключения дубликатов", "white")
        )
        while( filename := self.fileList.getNextFile()):
            # Необходимо вычленить файлы, которые одинаково называются без версий
            dfile = self.fileList.getFileStruct(self.fileList.getFullPath(filename))
            if not dfile.get("extension") in [".fb2", ".zip", ".epub", ".fb2.zip", ".fb2.epub", ".mobi"]:
                continue
            shortName = dfile.get("clearFileName") + dfile.get("extension")
            crc = dfile.get("crc32")
            book = self.takeBook(dfile)
            self.logger.debug("Краткое имя файла: \"%s\", CRC32: %i" % (shortName, crc))
            if book != None and book.is_dead():
                del book
                book = None
            if book != None:
                # переименование ниги, если отличается от реального или можно сохранить без версии
                newName = book.makeFileName()
                newFile = self.fileList.newFileIfExist(newName[0:-len(dfile.get("extension"))], dfile.get("extension"))
                #book.showBook()
                if newName != shortName or (newFile == newName and book.fileName() != newFile):
                    self.logger.debug("Переименование файла \"%s\" в \"%s\"" % (book.fileName(), newFile))
                    self.fileList.fileRename(book.fileName(), newFile)
                    book.filename = newFile
                    filename = newFile
                    dfile = self.fileList.getFileStruct(self.fileList.getFullPath(filename))
                    shortName = dfile.get("clearFileName") + dfile.get("extension")

            if shortName in files:
                ind = files.index(shortName)
                if crc == crc32List[ind]:
                    # Если файлы одинаковые (CRC32) - удалить дубликат #---, у которого длиннее имя
                    self.logger.info("Удаление дубликата %s" % self.fileList.getFullPath(filename))
                    print(
                        colored("[ДУБЛИКАТ]", "red", attrs = ["bold"]),
                        "Удаляю файл:", self.fileList.getFullPath(filename)
                    )
                    self.fileList.fileDelete(filename)
                    continue
                # Если файлы разные - проверить книги
                if book != None:
                    if books[ind] != None:
                        res = book.compareWith(books[ind])
                        self.logger.debug("Сравнение книг \"%s\" и \"%s\" с результатом %i" % (book.bookName(), books[ind].bookName(), res))
                        if res == 0:
                            self.logger.info("Удаление дубликата %s", self.fileList.getFullPath(filename))
                            print(
                                colored("[ДУБЛИКАТ]", "red", attrs = ["bold"]),
                                "Удаляю файл:", self.fileList.getFullPath(filename)
                            )
                            self.fileList.fileDelete(filename)
                            continue
                        if res == 10: # разные
                            self.logger.info("Добавление книги %s", self.fileList.getFullPath(filename))
                            files.append(shortName)
                            dfiles.append(dfile)
                            crc32List.append(crc)
                            books.append(book)
                            continue
                        if res < 0: # вторая полнее
                            self.logger.info("Удаление предыдущей версии файла: %s", self.fileList.getFullPath(filename))
                            print(
                                colored("[Предыдущая версия]", "red", attrs = ["bold"]),
                                "Удаляю файл:", self.fileList.getFullPath(filename)
                            )
                            self.fileList.fileDelete(filename)
                            continue
                        oldFile = dfiles[ind].get("fileName") + dfiles[ind].get("extension")
                        self.logger.info("Удаление предыдущей версии файла: %s", self.fileList.getFullPath(oldFile))
                        print(
                            colored("[Предыдущая версия]", "red", attrs = ["bold"]),
                            "Удаляю файл:", self.fileList.getFullPath(oldFile)
                        )
                        self.fileList.fileDelete(oldFile)
                        self.logger.info("Замена файла книги: %s на %s"% (self.fileList.getFullPath(filename), self.fileList.getFullPath(oldFile)))
                        print(
                            colored("[ЗАМЕНА (книги)]", "yellow", attrs = ["bold"]),
                            "Старый файл:", self.fileList.getFullPath(filename)
                        )
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
                    try:
                        self.logger.info("Удаляется файл: %s" % filename)
                        self.fileList.fileDelete(filename)
                        self.logger.info("Удалён файл: %s" % filename)
                    finally:
                        continue
                self.logger.info("Учитывается файл: %s" % filename)
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
            print(
                "%d" % self.fileList.getPercent(),
                "%", end="\r"
            )
            #print( "%d " % ((percent) * 100 // self.countfiles),"%", filename, self.countfiles)
            #self.checkFile(filename)
        print(
            colored("Проверка завершена", "green", attrs = ["bold"])
        )
        self.logger.info("Окончание работы")


Library = GoodBooks()
Library.start()
