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
import os
import zipfile

print("Приведение в порядок файлов книг")
print("Copyright (C) 2022 Дмитрий Добрышин dimkainc@mail.ru")

files = os.listdir(".")

for file in files:
  ext = ".fb2.epub"
  newext = ".epub"
  endext = len(ext)
  if file.lower().endswith(ext):
    os.rename(file, file[0:-endext]+newext)
    print("[EPUB] Файл переименован: "+file[0:-endext]+newext)

  if file.lower().endswith(".fb2"):
    archfile = zipfile.ZipFile(file[0:-4]+".fb2.zip", "w")
    archfile.write(file, compress_type=zipfile.ZIP_DEFLATED)
    archfile.close()
    os.remove(file)
    print("[FB2.ZIP] Файл сжат: "+file[0:-4]+".fb2.zip")
 