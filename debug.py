#!/bin/python3
DEBUG = True
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
