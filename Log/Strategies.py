import logging
from datetime import date


def DEFAULT(console_level=30,file_level=20, log_path="C:/Temp/Log/"):
    log_formatter = logging.Formatter('%(asctime)s: - %(module)s.%(funcName)s - %(levelname)s: <%(message)s>')
    stream_handler = logging.StreamHandler()
    stream_handler._name = "BasicConsole"
    stream_handler.setLevel(level=console_level)
    stream_handler.setFormatter(log_formatter)
    file_name = log_path.replace(".log", "."+str(date.today())+".log")
    file_handler = logging.FileHandler(file_name, mode="a")
    file_handler._name = "FileHandler"
    file_handler.file_name = file_name
    file_handler.setLevel(level=file_level)
    file_handler.setFormatter(log_formatter)
    return stream_handler, file_handler

def MAYA(console_level):
    import maya.utils
    log_formatter = logging.Formatter('%(asctime)s: - %(module)s.%(funcName)s - %(levelname)s: <%(message)s>')
    stream_handler = maya.utils.MayaGuiLogHandler()
    stream_handler._name = "MayaConsole"
    stream_handler.setLevel(level=console_level)
    stream_handler.setFormatter(log_formatter)
    return stream_handler

def COMP_CONTACT_SHEET(level, log_path):
    log_formatter = logging.Formatter('%(asctime)s: - %(name)s: - %(levelname)s: <%(message)s>')
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(level=level)
    stream_handler.setFormatter(log_formatter)
    file_handler = logging.FileHandler(log_path.replace(".log", "." + str(date.today()) + ".log"), mode="a")
    file_handler.setLevel(level=level)
    file_handler.setFormatter(log_formatter)
    return stream_handler, file_handler


def ASSET_BROWSER(level, log_path):
    log_formatter = logging.Formatter('%(asctime)s: - %(name)s: - %(levelname)s: <%(message)s>')
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(level=level)
    stream_handler.setFormatter(log_formatter)
    file_handler = logging.FileHandler(log_path, mode="w")
    file_handler.setLevel(level=level)
    file_handler.setFormatter(log_formatter)
    return stream_handler, file_handler
