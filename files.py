#!/bin/python3

# -*- coding: utf-8 -*-
#import os, sys, shutil, zipfile, datetime, zlib, time
import os, time, pathlib

class Files():
    """Класс взаимодействия с файлами"""

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
        self.directory = directory
        self.index = 0
        self.filesList = [f for f in os.listdir(self.directory) if os.path.isfile(os.path.join(self.directory, f))]
        self.filesList.sort()
        #for f in self.filesList:
        #    print("><><><", f)

    def Directory(self):
        """
        Рабочая диектория
        Возвращает
        ----------
        str
            Рабочий каталог размещения файлов
        """
        return self.directory

    def getPercent(self):
        """
        Число просмотренных файлов в % * 100
        Возвращает
        ----------
        int
            Процентное значение просмотренных файлов
        """
        return self.index * 100 // len(self.filesList)

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
        return os.path.join(self.directory, filename)

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
        return os.path.basename(fullpath)

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
        return fullpath.replace("\\", os.path.sep)

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
            return nameOfFile
        verList = [str(x) for x in [*range(9)]] + ["(", ")", " ", "_"]
        while ind > 0 and nameOfFile[ind] in verList:
            ind -= 1
        if ind == len(nameOfFile) - 1:
            return nameOfFile
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
        if ext in [".zip", ".rar", ".gz"]:
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
        """
        res = {}
        res.update({"extension": self.getFileExt(fullPath)})
        filename = self.getOnlyFile(fullPath)
        res.update({"fileName": filename[0:-len(res.get("extension"))]})
        res.update({"directory": os.path.dirname(fullPath)})
        res.update({"clearFileName": self.clearVersion(res.get("fileName"))})
        return res

    def addFile(self, fileName):
        """
        Добавление файла в конец списка файлов
        Параметры
        ---------
        filename : str
            Имя файла
        """
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
        newfile = "".join([fname, fext])
        while newfile.lower() in map(str.lower, self.filesList):
            num += 1
            newfile = "".join([fname, "_(%d)" % num, fext])
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
            return self.filesList[self.index - 1]
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

    def fileDelete(self, filename):
        """
        Удаляет файл и его запись в списке файлов
        Параметры
        ---------
        filename : str
            Имя файла с путём
        """
        fullfilename = self.getFullPath(filename)
        index = self.filesList.index(filename)
        os.remove(fullfilename)
        self.filesList.remove(filename)
        if index < self.index:
            self.index -= 1;
