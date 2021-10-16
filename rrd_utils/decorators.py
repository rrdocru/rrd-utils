# coding: utf-8
"""Модуль содержащий используемые внутри приложения декораторы"""
import gc
import logging
import warnings
from functools import wraps


logger = logging.getLogger(__name__)


def once(func):
    """
    Декоратор для единовременного вызова декорируемой функции

    :param func: декорируемая функция
    """
    @wraps(func)
    def inner(*args, **kwargs):
        if not inner.called:
            func(*args, **kwargs)
            inner.called = True
    inner.called = False
    return inner


def memoized(func):
    """
    Декоратор для сохранения результатов выполнения функции

    Все результаты выполнения сохраняются в локальном словаре

    :param func: вызываемая функция
    :return: результат выполнения
    """
    cache = {}

    @wraps(func)
    def inner(*args, **kwargs):
        key = args, tuple(sorted(kwargs.items()))
        if key not in cache:
            result = func(*args, **kwargs)
            if result:
                cache[key] = result
        return cache.get(key, None)
    return inner


def pre(cond, message):
    """
    Декоратор для проверки условий перед выполнением функции

    :param cond: функция для проверки значения
    :param str message: сообщение, если проверка завершилась неудачей
    """
    def wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            assert cond(*args, **kwargs), message
            return func(*args, **kwargs)
        return inner
    return wrapper


def post(cond, message):
    """
    Декоратор для проверки условий перед выполнением функции

    :param cond: функция для проверки значения
    :param str message: сообщение, если проверка завершилась неудачей
    """
    def wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            result = func(*args, **kwargs)
            assert cond(result), message
            return result
        return inner
    return wrapper


def collect(cond):
    """
    Декоратор вызывающий сборку мусора при установке соответствующего флага

    :param bool cond: включить после работы сборку мусора с выводом сообщений о количества несобранных объектов
    """
    def wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            gc_debug = gc.get_debug()
            gc_enabled = gc.isenabled()
            if cond:
                gc.disable()
                gc.set_debug(gc.DEBUG_LEAK)
            result = func(*args, **kwargs)
            if cond:
                print('{0} objects collected'.format(gc.collect()))
            gc.set_debug(gc_debug)
            if gc_enabled:
                gc.enable()
            return result
        return inner
    return wrapper


def deprecated(function_name):
    """
    Декоратор помечающий функцию как устаревшую

    :param str function_name: имя функции которая должна использоваться
    """
    def wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            warnings.warn_explicit(
                message='Вызываемая функция устарела. Используйте вместо неё {}'.format(function_name),
                category=DeprecationWarning,
                filename=func.__code__.co_filename,
                lineno=func.__code__.co_firstlineno + 1
            )
            return func(*args, **kwargs)
        return inner
    return wrapper
