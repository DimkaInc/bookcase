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
# Инициализация Colorama
init(autoreset = True)

now = datetime.datetime.now()
version = "1.1.0.32"
author = "Дмитрий Добрышин"
email = "dimkainc@mail.ru"

print(colored("Приведение в порядок файлов книг", "green", attrs = ["bold"]),
  colored("(v"+version+")", "red", attrs = ["bold"]))
print(colored("©", "yellow", attrs = ["bold"]), 
  colored("%d" % now.year + " " + author, "white", attrs = ["bold"]),
  colored(email, "cyan", attrs = ["bold", "underline"]), "\n")

files = os.listdir(".")
lenFiles = len(files)
files.sort()
crc32list = []

def crc32(filename, chunksize=65536):
  """Подсчёт CRC32 суммы для файла"""
  hash = 0
  with open(filename, "rb") as f:
    while (chunk := f.read(chunksize)):
      hash = zlib.crc32(chunk, hash)
  return "%08X" % (hash & 0xFFFFFFFF)

def existfile(nfile, ext):
  """Генерация имени фала, если совпадает с существующим"""
  global crc32list

  num = 0
  newfile = nfile + ext
  while os.path.exists(newfile):
    num += 1
    newfile = nfile + "(%d)" % num + ext
  return newfile

#allFilesCRC32 = []
"""Сбор CRC32 всех файлов"""
print(colored("Производится учёт всех существующих файлов для исключения дубликатов", "grey"))
percent = 0
for file in files:
  percent += 1
  print( "%d" % (percent * 100 // lenFiles), "%", end="\r")
  if (file.lower().endswith(".fb2.zip") or 
    (file.lower().endswith(".epub") and 
    not file.lower().endswith(".fb2.epub")) or 
    file.lower().endswith(".fb2")):
    fcrc32 = crc32(file)

    if fcrc32 in crc32list:
      os.remove(file)
      print(colored("[ДУБЛИКАТ]", "red", attrs = ["bold"]), "Удалён файл: " + file)
    else:
      crc32list.append(fcrc32)

files = os.listdir(".")
lenFiles = len(files)
files.sort()
percent = 0

for file in files:
  percent += 1
  print( "%d" % (percent * 100 // lenFiles), "%", end="\r")
  ext = ".fb2.epub"
  newext = ".epub"
  endext = len(ext)
  num = 0
  if file.lower().endswith(ext):
    mycrc32 = crc32(file)
    if mycrc32 in crc32list:
      os.remove(file)
      print(colored("[EPUB]", "red", attrs = ["bold"]), "Это дубликат: " +
        file)
    else:
      crc32list.append(mycrc32)
      newfile = existfile(file[0:-endext], newext)
      os.rename(file, newfile)
      print(colored("[EPUB]", "yellow", attrs = ["bold"]), "Файл переименован: " +
        newfile)

  if file.lower().endswith(".fb2"):
    newfile = existfile(file[0:-4], ".fb2.zip")
    archfile = zipfile.ZipFile(newfile, "w")
    archfile.write(file, compress_type=zipfile.ZIP_DEFLATED)
    archfile.close()
    os.remove(file)
    mycrc32 = crc32(newfile)
    if mycrc32 in crc32list:
      os.remove(newfile)
      print(colored("[FB2.ZIP]", "red", attrs = ["bold"]), "Это дубликат: " +
        file)
    else:
      crc32list.append(mycrc32)
      print(colored("[FB2.ZIP]", "green", attrs = ["bold"]), "Файл сжат: " +
        newfile)
 
