# coding: utf-8
"""Модуль содержащий дополнительные функции"""
import glob
import logging
import os
import zipfile
from shutil import copyfileobj, rmtree
from tempfile import TemporaryDirectory, mkdtemp
from rrd_utils.consts import DEFAULT_EXTENSION, DEFAULT_EXTENSION_ZIP, DEFAULT_EXTRACT_FILESIZE


logger = logging.getLogger(__name__)


def recurse_unzip(path, dir=None, extension=None, max_size=None):
    """
    Рекурсивное извлечение файлов из ахрива

    В случае если в архиве находится другой архив, то он извлекается в отдельную директорию со своим содержимым
    :param str path: полный путь к архиву или xml-документу
    :param str dir: пользовательская корневая директория для распаковки. По умолчанию `gettempdir()`
    :param list extension: список расширений файлов которые следует возвращать итератору
    :param int max_size: максимальный объем извлекаемого файла
    :return:
    """
    if not zipfile.is_zipfile(path):
        if not extension or (extension and os.path.splitext(path)[1] in extension):
            yield path
        return

    with TemporaryDirectory(prefix='rrd_', dir=dir) as tempdir:
        with zipfile.ZipFile(path) as _zipfile:
            for _name in sorted(_zipfile.namelist(), key=lambda _name: os.path.split(_name)):
                if max_size and _zipfile.getinfo(_name).file_size > max_size:
                    logger.warn('Очень большой файл. {:<5.2f} Mb. Будет пропущен. {}'.format(_zipfile.getinfo(_name).file_size / 1024 / 1024, path))
                    continue
                try:
                    _unicode_name = _name.encode('cp437').decode('cp866')
                except (UnicodeEncodeError, UnicodeDecodeError):
                    _unicode_name = _name
                _filename = os.path.basename(_name)
                if not _filename:
                    continue

                # Извлечение файла не через extract для того чтобы можно было извелекать файлы
                # которые в архиве находятся в директориях
                target_filename = os.path.join(tempdir, _unicode_name)
                os.makedirs(os.path.dirname(target_filename), exist_ok=True)
                target_fileobj = open(target_filename, mode="wb")
                source_fileobj = _zipfile.open(_name)

                with source_fileobj, target_fileobj:
                    copyfileobj(source_fileobj, target_fileobj)

                if os.path.splitext(_filename)[1] not in [DEFAULT_EXTENSION_ZIP, ] + (extension or []):
                    continue

                yield from recurse_unzip(os.path.abspath(os.path.join(tempdir, _unicode_name)), dir, extension)


def rrd_file_iterator(pattern, recursive=True, dir=None, extension=None, max_size=None):
    """
    Функция возвращающая xml-документы из директории, архивов, архивов в архивах

    `pattern` шаблон для поиска файлов/директорий используемый в функции *glob*.
    Если pattern заканчивается на /* то в поиске будут и файлы и директории
    Если pattern заканчивается на /*.* то в поиске будут только файлы

    По умолчанию поиск рекурсивный по всем вложенным директориям
    Файлы и директории начинающиеся с . по умолчанию пропускаются

    :param str pattern: паттерн для отбора файлов
    :param bool recursive: использовать рекурсивный поиск
    :param str dir: пользовательская корневая директория для распаковки. По умолчанию `gettempdir()`
    :param list extension: список расширений файлов которые следует возвращать итератору
    :param int max_size: максимальный размер файла которые будут извлекаться из архивов
    :return: итератор по полным путям к файлам
    """
    if not extension:
        extension = [DEFAULT_EXTENSION, ]
    for path in glob.iglob(pattern, recursive=recursive):
        # Т.к. по умолчанию поиск рекурсивный, то нет смысла определять директория это или файл
        # При рекурсивном поиске файлы из вложенных директорий тоже будут извлечены
        if os.path.isdir(path):
            continue
        yield from recurse_unzip(path, dir=dir, extension=extension, max_size=max_size)


def rrd_file_iterator_with_origin_name(pattern, recursive=True, dir=None, extension=None, max_size=None):
    """
    Функция возвращающая xml-документы из директории, архивов, архивов в архивах и имена исходных архивов

    `pattern` шаблон для поиска файлов/директорий используемый в функции *glob*.
    /* : в поиске будут и файлы и директории в текущей директории
    /*.* : в поиске будут только файлы в текущей директории
    /**/*.* : в поиске файлы во всех вложенных директориях

    По умолчанию поиск рекурсивный по всем вложенным директориям
    Файлы и директории начинающиеся с . по умолчанию пропускаются

    :param str pattern: паттерн для отбора файлов
    :param bool recursive: использовать рекурсивный поиск
    :param str dir: пользовательская корневая директория для распаковки. По умолчанию `gettempdir()`
    :param list extension: список расширений файлов которые следует возвращать итератору
    :param int max_size: максимальный размер файла которые будут извлекаться из архивов
    :return: итератор по полным путям к файлам
    """
    if not extension:
        extension = [DEFAULT_EXTENSION, ]
    for path in glob.iglob(pattern, recursive=recursive):
        # Т.к. по умолчанию поиск рекурсивный, то нет смысла определять директория это или файл
        # При рекурсивном поиске файлы из вложенных директорий тоже будут извлечены
        if os.path.isdir(path):
            continue
        for path_output in recurse_unzip(path, dir=dir, extension=extension, max_size=max_size):
            yield path_output, path


def recurse_unzip_without_yield(path, dir_=None, extensions=None, max_size=None):
    """
    Рекурсивное извлечение файлов из ахрива

    В случае если в архиве находится другой архив, то он извлекается в отдельную директорию со своим содержимым
    :param str path: полный путь к архиву или xml-документу
    :param str dir_: пользовательская корневая директория для распаковки. По умолчанию `gettempdir()`
    :param list extensions: список расширений файлов которые следует возвращать итератору
    :param int max_size: максимальный объем извлекаемого файла
    :return: список файлов
    :rtype: list
    """
    result = []
    if not zipfile.is_zipfile(path):
        if not extensions or (extensions and os.path.splitext(path)[1] in extensions):
            result.append(path)
            return result

    tempdir = mkdtemp(prefix='rrd_', dir=dir_)
    with zipfile.ZipFile(path) as _zipfile:
        for _name in sorted(_zipfile.namelist(), key=lambda _name: os.path.split(_name)):
            if max_size and _zipfile.getinfo(_name).file_size > max_size:
                logger.warn('Очень большой файл. {:<5.2f} Mb. Будет пропущен. {}'.format(_zipfile.getinfo(_name).file_size / 1024 / 1024, path))
                continue
            try:
                _unicode_name = _name.encode('cp437').decode('cp866')
            except (UnicodeEncodeError, UnicodeDecodeError):
                _unicode_name = _name
            _filename = os.path.basename(_name)
            if not _filename:
                continue

            # Извлечение файла не через extract для того чтобы можно было извелекать файлы
            # которые в архиве находятся в директориях
            target_filename = os.path.join(tempdir, _unicode_name)
            os.makedirs(os.path.dirname(target_filename), exist_ok=True)
            target_fileobj = open(target_filename, mode="wb")
            source_fileobj = _zipfile.open(_name)
            try:
                with source_fileobj, target_fileobj:
                    copyfileobj(source_fileobj, target_fileobj)
            finally:
                target_fileobj.close()
                source_fileobj.close()

            if os.path.splitext(_filename)[1] not in [DEFAULT_EXTENSION_ZIP, ] + (extensions or []):
                continue
            else:
                result += recurse_unzip_without_yield(os.path.abspath(os.path.join(tempdir, _unicode_name)), dir_=dir_, extensions=extensions)
    return result
