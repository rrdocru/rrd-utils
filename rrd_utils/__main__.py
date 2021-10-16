# coding: utf-8
import logging
from rrd_utils import rrd_file_iterator


logger = logging.getLogger(__name__)


def createParser():
    """
    Объявление параметров командной строки

    :return: объект с определенными параметрами
    :rtype: argparse.ArgumentParser
    """
    import argparse  # noqa
    parser = argparse.ArgumentParser()

    parser.add_argument('-i', '--input',
                        help='Шаблон пути для поиска файлов',
                        type=str,
                        required=True
                        )
    parser.add_argument('-r', '--recursive',
                        help='Рекурсивный обход при поиске по паттерну',
                        action='store_false')
    return parser


def main():
    parser = createParser()
    args = parser.parse_args()
    pattern = args.input
    for file_ in rrd_file_iterator(pattern, args.recursive):
        logger.debug(file_)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    main()
