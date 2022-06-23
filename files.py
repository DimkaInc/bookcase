#!/bin/python3

# -*- coding: utf-8 -*-
#import os, sys, shutil, zipfile, datetime, zlib, pathlib, time
import os

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

    def addFile(self, fileName):
        """
        Добавление файла в конец списка файлов
        Параметры
        ---------
        filename : str
            Имя файла
        """
        self.filesList.append(os.path.join(self.directory, fileName))

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
        while os.path.join(self.directory, newfile).lower() in map(str.lower, self.filesList):
            num += 1
            newfile = "".join([fname, "_(%d)" % num, fext])
        return newfile

    def getNextFile(self):
        """
        Возвращает следующий файл из хранимого списка или False. Указатель передвигает на следующий по списку файл
        Возврашает
        ----------
        str | False
            Полный путь к файлу или False если больше файлов нет
        """
        if self.index < self.filesList.length:
            self.index += 1
            return self.filesList[self.index - 1]
        return False

    def setFileDateTime(self, filename, date_time):
        """
        Устанавливает файлу указанные дату и время
        Параметры
        ---------
        filename : str
            Полный путь к файлу
        date_time : datetime
            Дата и время создния файла
        """
        date_time = time.mktime(date_time + (0, 0, -1))
        os.utime(filename, (date_time, date_time))

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
        fullfilename = os.path.join(self.directory, filename)
        fullnewfilename = os.path.join(self.directory, newfilename)
        os.rename(fullfilename, fullnewfilename)
        self.filelist[self.filelist.index(fullfilename)] = fullnewfilename

    def fileDelete(self, filename):
        """
        Удаляет файл и его запись в списке файлов
        Параметры
        ---------
        filename : str
            Имя файла
        """
        fullfilename = os.path.join(self.directory, filename)
        index = self.filelist.index(fullfilename)
        os.remove(fullfilename)
        self.filelist.remove(fullfilename)
        if index < self.index:
            self.index -= 1;
