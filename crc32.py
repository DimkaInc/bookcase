#!/bin/python3
import zlib, logging
# -*- coding: utf-8 -*-


class Crc32:
    logger = logging.getLogger("crc32")
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
        result = zlib.crc32(chunk, hash)
        self.logger.debug("crc32(..,%i)= %i" % (hash, result))
        return result

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
        self.logger.info("crc32file(%s, %i)= %i" % (filename, chunksize, hash))
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
        result = "%08X" % (hash & 0xFFFFFFFF)
        self.logger.debug("hash2crc32(%i)= %s" % (hash, result))
        return result