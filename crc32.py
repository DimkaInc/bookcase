#!/bin/python3
import zlib

class Crc32:
    """Подсчёт CRC32 суммы для файла"""

    def crc32(self, filename, chunksize=65536):

        hash = 0
        with open(filename, "rb") as f:
            while (chunk := f.read(chunksize)):
                hash = zlib.crc32(chunk, hash)
        return "%08X" % (hash & 0xFFFFFFFF)
