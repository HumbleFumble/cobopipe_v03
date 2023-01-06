import logging
from Log.Strategies import DEFAULT, MAYA
from os.path import exists
from os import mkdir


MAIN_LOGGER_NAME = "MainLogger"
LOGGING_PATH = "C:\\Temp\\logs\\"

try:
    import maya.utils
    in_maya = True
except:
    in_maya = False


def clearLog(logger):
    logger.handlers.clear()


def setFileLevel(logger, level=20):
    """
    DESCRIPTION:
    Input a logger object and set its logging level for file printouts.
    see https://docs.python.org/3/library/logging.html for more information about logging.

    LOGGING LEVELS:
        0  = NOTSET
        10 = DEBUG
        20 = INFO
        30 = WARNING
        40 = ERROR
        50 = CRITICAL

    :param logger: logging.logger object to have it's level set.
    :param level: integer value between 0 - 50, with step 10.
    :return: logging.logger object with new level set.
    """
    for i in logger.handlers:
        if i.name == "FileHandler":
            i.setLevel(level)

def getFileLevel(logger):
    for i in logger.handlers:
        if i.name == "FileHandler":
            return i.level

def getConsoleLevel(logger):
    for i in logger.handlers:
        if i.name  == "BasicConsole":
            return i.level

def setConsoleLevel(logger, level=30):
    """
    DESCRIPTION:
    Input a logger object and set its logging level for console printouts.
    see https://docs.python.org/3/library/logging.html for more information about logging.

    LOGGING LEVELS:
        0  = NOTSET
        10 = DEBUG
        20 = INFO
        30 = WARNING
        40 = ERROR
        50 = CRITICAL

    :param logger: logging.logger object to have it's level set.
    :param level: integer value between 0-50, with step 10.
    :return: logging.logger object with new level set.
    """
    for i in logger.handlers:
        if i.name in ["BasicConsole", "MayaConsole"]:
            i.setLevel(level)




def getLogger(name=None, log_path=None, console_level=30, log_strategy=None):
    """
    DESCRIPTION:
    This function wraps the business of the logging module. It automates the process of assigning handlers and
    formatters to the logger object. Also once a logging object is made a main logger is made as its parent for
    automated inheritance of handlers.
    see https://docs.python.org/3/library/logging.html for more information about logging.

    USAGE:
    Call getLogger() to get a simple logger object. Functionality should be plug and play from there. To mute logging
    in terminal, create the logger with log_level=logging.WARNING to only display warning messages.
        The logger object is from the logging module and is used to create logging messages of different severities.

    LOGGING LEVELS:
        0  = NOTSET
        10 = DEBUG
        20 = INFO
        30 = WARNING
        40 = ERROR
        50 = CRITICAL

    :param name:            Define the name of the logger object you are creating. No name will summon the MainLogger.
    :param log_path:        Define where the file logs should be outputted. No path will direct to default path.
    :param console_level:       Refers to the levels of logging severity. Check out the logging module for levels.
    :param log_strategy:    Define behavior of logging handlers. Strategies are defined in the Strategies module.
    :return:                Returns a plain old Logger type object from the built-in logging module.
    """
    if name and not isinstance(name, str):
        raise TypeError("Parameter 'name' must be of type 'str'")
    elif name and any(i in "\\/:*?\"<>|" for i in name):
        raise NameError("Name for logger ( "+name+" ) must not contain any of the following characters \\/:*?\"<>|")

    if not exists(LOGGING_PATH):
        mkdir(LOGGING_PATH)

    if not logging.getLogger(MAIN_LOGGER_NAME).handlers:
        """CREATE A MAIN LOGGER IF NOT EXISTING"""
        if not log_path:
            log_path = LOGGING_PATH + "main.log"
        create_logger(name=MAIN_LOGGER_NAME, log_path=log_path, console_level=console_level, log_strategy=log_strategy)

    #check if we are in maya:

    if name == MAIN_LOGGER_NAME or not name:
        """RETURN MAIN LOGGER"""
        cur_logger = logging.getLogger(name=MAIN_LOGGER_NAME)
        # checkHandlers(cur_logger)
        return cur_logger

    elif name:
        """RETURN A CHILD LOGGER"""
        logger_name = MAIN_LOGGER_NAME + "." + name
        if not log_path:
            log_path = LOGGING_PATH + logger_name + ".log"

        if logging.getLogger(logger_name).handlers:
            """GET EXISTING CHILD LOGGER"""
            return logging.getLogger(logger_name)
        else:
            """CREATE A CHILD LOGGER"""
            if not log_strategy:
                return create_inheriting_logger(name=logger_name)
            else:
                return create_logger(name=logger_name, log_path=log_path, console_level=console_level, log_strategy=log_strategy)

def buildNewLog(logger):
    from datetime import date
    import os
    org_log_path = "%smain.%s.log" %(LOGGING_PATH,str(date.today()))
    if not os.path.exists(org_log_path):
        return False
    for v in range(1,20):
        version_number = v
        file_name = "%smain.%s_V%s.log" %(LOGGING_PATH,str(date.today()),version_number)
        if not os.path.exists(file_name):
            break
    for i in logger.handlers:
        if i.name == "FileHandler":
            i.close()
    os.rename(org_log_path,file_name)
    logger.warning("--Building clean log--")


# def checkHandlers(logger):
#     found = False
#     maya_handle = None
#     cur_level = 30
#     for ci in logger.handlers:
#         if ci.name == "MayaConsole":
#             found = True
#             maya_handle = ci
#         if ci.name == "BasicConsole":
#             cur_level = ci.level
#     if in_maya:
#         if found:
#             return True
#         else:
#             logger.addHandler(MAYA(cur_level))
#     else:
#         if found:
#             logger.removeHandler(logger.handle(maya_handle))



def refreshLogger(reset_logger=False):
    """
    used to reboot the logger handles so it will show in maya script editor instead of the output window.
    :param reset_logger: true/false will reset the logger to default handler values
    :return:
    """
    if reset_logger:
        cur_logger = create_logger(name=MAIN_LOGGER_NAME, log_path="%smain.log" % LOGGING_PATH, log_strategy=None)
        return cur_logger
    console_level =  getConsoleLevel(logging.getLogger(MAIN_LOGGER_NAME))
    file_level = getFileLevel(logging.getLogger(MAIN_LOGGER_NAME))
    cur_logger = create_logger(name=MAIN_LOGGER_NAME,log_path="%smain.log" % LOGGING_PATH,console_level=console_level,file_level=file_level,log_strategy=None)
    return cur_logger

def create_logger(name=None, log_path=None, console_level=30,file_level=20, log_strategy=None):
    """DO NOT CALL THIS! IT IS UTILITY FOR getLogger()"""
    if not log_strategy:
        log_strategy = DEFAULT
    stream_handler, file_handler = log_strategy(console_level=console_level,file_level=file_level,log_path=log_path)
    logger = logging.getLogger(name=name)  # Sets Logger's stream handler levels. File handler is DEBUG as default.
    logger.propagate = False

    for f in range(len(logger.handlers)-1,-1,-1):
        i = logger.handlers[f]
        i.flush()
        i.close()
        logger.removeHandler(i)

    logger.setLevel(level=logging.DEBUG)  # !IMPORTANT! this MUST be of type DEBUG, else it will block handlers.
    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)
    # if in_maya:
    #     logger.addHandler(MAYA(console_level=console_level))
    logger.strategy = log_strategy
    logger.debug("~"*125)
    return logger


def create_inheriting_logger(name):
    """DO NOT CALL THIS! IT IS UTILITY FOR getLogger()"""
    logger = logging.getLogger(name=name)
    logger.strategy = logger.parent.strategy
    return logger
