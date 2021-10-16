# coding: utf-8
"""Модуль, содержащий общие дополнительные классы"""
import csv


class ITT(csv.Dialect):
    """
    Dialect для выгрузки в CSV.

    * Разделитель  -- ';'
    * Перенос строк  -- '\n'
    * Символ экранирования -- '"'
    * Режим экранирования -- ALL
    """
    delimiter = ';'
    quotechar = '"'
    doublequote = True
    skipinitialspace = False
    lineterminator = '\n'
    quoting = csv.QUOTE_ALL
