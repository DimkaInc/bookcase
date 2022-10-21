#!/bin/python3

# -*- coding: utf-8 -*-
#import os, sys, shutil, zipfile, datetime, zlib, time
import os, time, pathlib, logging
import magic
from crc32 import Crc32

class Files():
    """Класс взаимодействия с файлами"""

    logger = logging.getLogger("files")
    filesList = []
    index = 0 # Указатель на следующий файл из списка
    directory = "."

    def __init__(self, directory):
        """
        Получение списка файлов из указанной дирректории
        Параметры
        ----------
        directory : str
            каталог, в коором будет производиться работа
        """
        self.logger.info("Создан класс")
        self.logger.debug("Каталог: %s" % directory)
        self.directory = directory
        self.index = 0
        self.filesList = [f for f in os.listdir(self.directory) if os.path.isfile(os.path.join(self.directory, f))]
        self.filesList.sort()

    def getFileAndExts(self, filename):
        """
        Возврашает имя файла и тип (типы) в списке
        Параметры
        ---------
        filename : string
            Имя файла

        Возвращает
        ----------
        Dict
            Список строк: имя файла, тип/типы
        """
        suffixes = "".join(pathlib.Path(filename).suffixes)
        return filename[:-len(suffixes)], suffixes

    def unique_file(self, fullFilename):
        """
        Формирует уникальное имя. Если такое имя уже есть, создаёт новое в формате filename_(\d).ext
        Параметры
        ---------
        fullFileName : string
            имя файла с путём

        Возвращает
        ----------
        string
            Имя файла с путём, уникальное в каталоге
        """
        fname, fext = self.getFileAndExts(fullFilename)
        if len("".join([fname, fext])) > 100:
            fname = fname[:100 - len(fext)]
        fnum = ""
        findex = 0
        while os.path.exists(fname + fnum + fext):
            findex += 1
            fnum = "_(" + str(findex) + ")"
        return fname + fnum + fext

    def to_unichr(self, str):
        """
        Преобразуетс строку вида \d[3] в символ
        Параметры
        ---------
        str : string
            строка

        Возвращает
        ----------
        char
            символ
        """
        oct = int(str.group(1), 8)
        return chr(oct)


    def getContentExt(self, fileName):
        """
        Определяет тип файла по содержимому.
        Параметры
        ---------
        fileName : string
            путь к файлу

        Возвращает
        ----------
        Dict
            Список. Имя файла без последнего расширения, его расширние, 
            расширение, определённое по содержимому или None
        """
        fname, fext = os.path.splitext(fileName)
        k = magic.detect_from_filename(fileName)
        # Каталог
        if "directory" in k.name:
            return None

        # текстовые документы
        if ("text" in k.mime_type):
            ftype = k.mime_type[5:]

            # .xml - Структурированный файл
            # .fb2 - Fiction Book - электронная книга
            # .fbd - Fiction Book Description - Файл-описание электроннй книги (Файл спутник для PDF, DjVu CHM, TXT, DOC и других)
            if (ftype == "xml"):
                return fname, fext, ".fb2"

            # .py - python script
            if "python" in ftype:
                return fname, fext, ".txt"

            # .txt - текстовый файл
            if ("plain" in ftype):
                return fname, fext, ".txt"

            # .rtf - текстовый файл
            if ("rtf" in ftype):
                return fname, fext, ".rtf"

        if "application" in k.mime_type:
            ftype = k.mime_type[12:]

            # .zip - архив
            if ftype == "zip":
                return fname, fext, ".zip"

            # .pdf - Электронная книга
            if "pdf" in ftype:
                return fname, fext, ".pdf"

            # .epub - Электронная книга
            if "epub" in ftype:
                return fname, fext, ".epub"

            # .doc - MSOffice документ
            if "msword" in ftype:
                return fname, fext, ".doc"

            # .docx - MSOffice документ
            if ("openxmlformats-officedocument" in ftype) and ("Microsoft Word 2007+" in k.name):
                return fname, fext, ".docx"

            # .iso - образ CD или DVD
            if "iso" in ftype:
                return fname, fext, ".iso"

            # .xml - Структурированный файл
            # .fb2 - Fiction Book - электронная книга
            # .fbd - Fiction Book Description - Файл-описание электроннй книги (Файл спутник для PDF, DjVu CHM, TXT, DOC и других)
            if ftype == "xml":
                return fname, fext, ".fb2"

            # .fb2 - электронная книга - Странно, что такой тип данных встречается. Наверно много иллюстраций
            if "octet-stream" in ftype and "data" in k.name:
                return fname, fext, ".fb2"

            # .chm - Windows Help
            if "octet-stream" in ftype and "HtmlHelp Data" in k.name:
                return fname, fext, ".chm"

            # .docx - Старый формат документа OXML
            if "octet-stream" in ftype and "Microsoft OOXML" in k.name:
                return fname, fext, ".docx"

            # .mobi - электронная книга
            if "octet-stream" in ftype and "Mobipocket E-book" in k.name:
                return fname, fext, ".mobi"

            # AppleDouble encoded
            if "octet-stream" in ftype and "AppleDouble encoded" in k.name and fname[0] == "." and fext in [".fb2", ".epub", ".doc", ".docx", ".xls", ".txt", ".fbd"]:
                return fname, fext, ".virus"
        #
        # Изображения
        #
        if "image" in k.mime_type:
            ftype = k.mime_type[6:]

            # .DjVu - Фрактальное изображение
            if "djvu" in ftype:
                return fname, fext, ".djvu"

            # .DjVu - Фрактальное изображение
            if "jpeg" in ftype:
                return fname, fext, ".jpg"
        #
        # Аудио
        #
        if "audio" in k.mime_type:
            ftype = k.mime_type[6:]
            if "mpeg" in ftype and "layer III" in k.name:
                return fname, fext, ".mp3"
        #
        # Видео
        #
        if "video" in k.mime_type:
            ftype = k.mime_type[6:]
            if "mp4" in ftype:
                return fname, fext, ".mp4"

        return fname, fext, ".uncnown"

    def Directory(self):
        """
        Рабочая диектория
        Возвращает
        ----------
        str
            Рабочий каталог размещения файлов
        """
        self.logger.debug("Directory()= %s" % self.directory)
        return self.directory

    def getPercent(self):
        """
        Число просмотренных файлов в % * 100
        Возвращает
        ----------
        int
            Процентное значение просмотренных файлов
        """
        result = self.index * 100 // len(self.filesList)
        self.logger.debug("getPercent()= %i" % result)
        return result

    def getFullPath(self, filename):
        """
        Добавляет к имени файла рабочую директорию
        Параметры
        ---------
        filename : str
            Имя файла без пути

        Возвращает
        ----------
        str
            имя файла с путём к рабочей папке

        """
        result = os.path.join(self.directory, filename)
        self.logger.debug("getFullPath(%s)= %s" % (filename, result))
        return result

    def getOnlyFile(self, fullpath):
        """
        Возвращает имя файла без директории
        Параметры
        ---------
        fullpath : str
            Полный путь к файлу

        Возвращает
        ----------
        str
            Имя файла без пути
        """
        result = os.path.basename(fullpath)
        self.logger.debug("getOnlyFile(%s)= %s" % (fullpath, result))
        return result

    def getOsSeparatorPath(self, fullpath):
        """
        Заменяет разделители "\\" в пути на используемые в ОС
        Параметры
        ---------
        fullpath : str
            Полный путь к файлу
        Возвращает
        ----------
        str
            Полный путь к файлу с разделителями пути, используемыми в ОС запуска приложения
        """
        result = fullpath.replace("\\", os.path.sep)
        self.logger.debug("getOsSeparatorPath(%s)= %s" % (fullpath, result))
        return result

    def clearVersion(self, nameOfFile):
        """
        Возвращает имя файла без версии
        Параметры
        ---------
        nameOfFile : str
            Имя файла без расширения

        Возвращает
        ----------
        str
            Имя файла без версии и расширения
        """
        ind = len(nameOfFile) - 1
        if ind < 0 or not nameOfFile[ind] in [")"]:
            self.logger.debug("clearVersion(%s)= %s" % (nameOfFile, nameOfFile))
            return nameOfFile
        ind -= 1
        verList = [str(x) for x in list(range(10))]
        while ind > 0 and nameOfFile[ind] in verList:
            ind -= 1
        while ind > 0 and nameOfFile[ind] in ["_", "("]:
            ind -= 1
        if ind == len(nameOfFile) - 2:
            self.logger.debug("clearVersion(%s)= %s" % (nameOfFile, nameOfFile))
            return nameOfFile
        self.logger.debug("clearVersion(%s)= %s" % (nameOfFile, nameOfFile[0:ind + 1]))
        return nameOfFile[0:ind + 1]

    def getFileExt(self, filename):
        """
        Возвращает расширение файла
        Параметры
        ---------
        filename : str
            Имя файла с расширением

        Возвращает
        ----------
        str
            расширение файла (может быть двойное)
        """
        ext = pathlib.Path(filename).suffix
        if ext in [".zip", ".rar", ".gz", ".epub"]:
            filename = filename[0:-len(ext)]
            if filename.rfind(".") > -1:
                eend = pathlib.Path(filename).suffix
                if eend in [".fb2", ".tar", ".txt", ".rtf"]:
                    ext = eend + ext
        return ext

    def getFileStruct(self, fullPath):
        """
        Разбивает файл на составляющие элементы
        Параметры
        ---------
        fullPath : str
            Полное имя файла с путём

        Возвращает
        ----------
        dict
            Словарь со структурой файла
            "directory" : str
                Каталог размещения файла
            "fileName" : str
                Имя файла без расширения
            "clearFileName" : str
                Имя файла без версии и расширения
            "extension" : str
                Расширение (тип) файла
            "crc32" : str
                Контрольная сумма файла
        """
        res = {}
        res.update({"extension": self.getFileExt(fullPath)})
        filename = self.getOnlyFile(fullPath)
        res.update({"fileName": filename[0:-len(res.get("extension"))]})
        res.update({"directory": os.path.dirname(fullPath)})
        res.update({"clearFileName": self.clearVersion(res.get("fileName"))})
        try:
            res.update({"crc32": Crc32().crc32File(fullPath)})
        except:
            self.logger.error("Не удалось расчитать CRC32 для файла %s" % fullPath)
            res.update({"crc32": 0})
        self.logger.debug("getFileStruct(%s)= %s" % (fullPath, str(res)))
        return res

    def addFile(self, fileName):
        """
        Добавление файла в конец списка файлов
        Параметры
        ---------
        filename : str
            Имя файла
        """
        self.logger.debug("addFile(%s)" % fileName)
        self.filesList.append(fileName)

    def newFileIfExist(self, fname, fext):
        """
        Проверяет имя файла и если такой уже есть, то генерирует версию
        Параметры
        ---------
        fname : str
            Имя файла без расширения
        fext : str
            Расширение файла
        Возвращает
        ----------
        str
            Свободное имя файла с расширением
        """
        num = 0
        fname, fext = self.getFileAndExts("".join([fname, fext]))
        if len("".join([fname, fext])) > 100:
            fname = fname[:100 - len(fext)]
        newfile = "".join([fname, fext])
        while newfile.lower() in map(str.lower, self.filesList):
            num += 1
            newfile = "".join([fname, "_(%d)" % num, fext])
        self.logger.debug("newFileIfExist(%s, %s)= %s" % (fname, fext, newfile))
        return newfile

    def getNextFile(self):
        """
        Возвращает следующий файл из хранимого списка или False. Указатель передвигает на следующий по списку файл
        Возврашает
        ----------
        str | False
            Имя файла или False если больше файлов нет
        """
        if self.index < len(self.filesList):
            self.index += 1
            self.logger.debug("getNextFile()= %s" % self.filesList[self.index - 1])
            return self.filesList[self.index - 1]
        self.logger.debug("getNextFile()= False")
        return False

    def setFileDateTime(self, filename, date_time):
        """
        Устанавливает файлу указанные дату и время
        Параметры
        ---------
        filename : str
            Имя файла
        date_time : datetime
            Дата и время создния файла
        """
        date_time = time.mktime(date_time.timetuple())
        os.utime(self.getFullPath(filename), (date_time, date_time))
        self.logger.debug("setFileDateTime(%s, %s)" % (filename, str(date_time)))

    def fileRename(self, filename, newfilename):
        """
        Переименовывает filename в newfilename и вносит такие же изменения в список файлов
        Параметры
        ---------
        filename : str
            Имя файла
        newfilename : str
            Новое имя файла
        """
        os.rename(self.getFullPath(filename), self.getFullPath(newfilename))
        self.filesList[self.filesList.index(filename)] = newfilename
        self.logger.debug("fileRename(%s, %s)" % (filename, newfilename))

    def fileDelete(self, filename):
        """
        Удаляет файл и его запись в списке файлов
        Параметры
        ---------
        filename : str
            Имя файла с путём
        """
        fullfilename = self.getFullPath(filename)
        try:
            index = self.filesList.index(filename)
            os.remove(fullfilename)
            self.filesList.remove(filename)
            if index < self.index:
                self.index -= 1;
            self.logger.debug("fileDelete(%s)" % filename)
        except:
            self.logger.debug("fileDelete(%s) except!" % filename)
