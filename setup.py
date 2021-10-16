# coding: utf-8
import setuptools
from rrd_utils import name as package_name, version as package_version

with open('README.md', 'r', encoding='utf-8') as fn:
    long_description = fn.read()

setuptools.setup(
    name=package_name,
    version=package_version,
    description='Дополнительные функции и классы для пакетов RRDoc.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/rrdocru/rrd-utils.git',
    author='IT-Thematic',
    author_email='inbox@it-thematic.ru',
    classifiers=[
        'Development Status :: 5 - Production/Stable'
        'Operating System :: OS Independent',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)'
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8'
    ],
    packages=setuptools.find_packages(exclude=['examples', 'tests']),
    install_requires=[],
    python_requires='~=3.6',
    include_package_data=True,
)
