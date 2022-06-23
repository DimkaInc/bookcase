#!/bin/python3
import zlib

class Crc32:
    """Класс подсчёта контрольной суммы CRC32"""

    def crc32(self, chunk, hash = 0):
        """
        Подсчёт контрольно суммы для буфера
        Параметры
        ---------
        chunk : chunk
            Массив данных (строка)
        hash : int
            Контрольная сумма CRC32 предыдущего блока
            по умолчанию = 0

        Возвращает
        ----------
        int
            Контрольная сумма CRC32
            Чтобы привести к шестнадцатиричному виду используйте метод
            hash2crc32
        """
        return zlib.crc32(chunk, hash)

    def crc32File(self, filename, chunksize=65536):
        """
        Подсчёт контрольной суммы файла
        Параметры
        ---------
        filename : str
            Имя файла с путём
        chunksize : int
            Размер массива данных для блочного чтения
            по умолчанию 65536

        Возвращает
        ----------
        int
            Контрольная сумма CRC32
        """
        hash = 0
        with open(filename, "rb") as f:
            while (chunk := f.read(chunksize)):
                hash = self.crc32(chunk, hash)
        return hash

    def hash2crc32(self, hash):
        """
        Преобразование контрольной суммы CRC32 к шестнадцатиричному виду
        Параметры
        ---------
        hash : int
            Контрольная сумма CRC32

        Возвращает
        ----------
        str
            Контрольканя сумма в шестнадцатиричном виде
        """
        return "%08X" % (hash & 0xFFFFFFFF)