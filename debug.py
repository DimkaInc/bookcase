#!/bin/python3
"""
Модуль для отладки приложения.
В приложении необходимо импортировать logging и выполнить основную настройку.
Например:
logging.basicConfig(
    filename = sys.argv[0]+".log", # Имя файла для записи логов
    encoding = "utf-8",            # Кодировка внутри файла
    format = '%(asctime)s %(name)s[%(levelname)s]:%(message)s', # Формат строки записи лога
    filemode = "w", # режим перезаписи файла логов (без него дописывается в конец)
    datefmt = '%d.%m.%Y %H:%M:%S', # Формат времени
    level = logging.DEBUG          # Уровень логирования
) # DEBUG INFO WARNING ERROR CRITICAL - перечислены все уровни логирования, включает в себя и то, что правее

"""
def debuglog(message):
    import inspect, os, logging
    fnc = inspect.currentframe().f_back
    func = fnc.f_code
    logging.debug("\"%s\": %s в %s:%i" % (
        message,
        func.co_name,
        os.path.basename(func.co_filename),
        fnc.f_lineno # func.co_firstlineno
    ))
def infolog(message):
    import logging
    logging.info("\"%s\"" % (
        message
    ))
def warninglog(message):
    import inspect, os, logging
    fnc = inspect.currentframe().f_back
    func = fnc.f_code
    logging.warning("\"%s\": %s в %s:%i" % (
        message,
        func.co_name,
        os.path.basename(func.co_filename),
        fnc.f_lineno # func.co_firstlineno
    ))
def errorlog(message):
    import inspect, os, logging
    fnc = inspect.currentframe().f_back
    func = fnc.f_code
    logging.error("\"%s\": %s в %s:%i" % (
        message,
        func.co_name,
        os.path.basename(func.co_filename),
        fnc.f_lineno # func.co_firstlineno
    ))
def criticallog(message):
    import inspect, os, logging
    fnc = inspect.currentframe().f_back
    func = fnc.f_code
    logging.critical("\"%s\": %s в %s:%i" % (
        message,
        func.co_name,
        os.path.basename(func.co_filename),
        fnc.f_lineno # func.co_firstlineno
    ))
