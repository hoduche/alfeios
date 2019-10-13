# -*- coding: UTF-8 -*-

import re

from setuptools import setup, find_packages


def find_readme():
    with open('README.md', encoding='utf-8') as readme_file:
        return readme_file.read()


def find_requirements():
    with open('requirements.txt', encoding='utf-8') as requirements_file:
        return [each_line.strip() for each_line in requirements_file.read().splitlines()]


def find_version():
    with open('fs_crawler/__init__.py', encoding='utf-8') as version_file:
        pattern = '^__version__ = [\'\"]([^\'\"]*)[\'\"]'
        match = re.search(pattern, version_file.readline().strip())
        if match:
            return match.group(1)


setup(
    name='fs-crawler',
    version=find_version(),
    description='Crawl your filesystem to check duplicated files',
    long_description=find_readme(),
    long_description_content_type='text/markdown',
    url='https://github.com/hoduche/fs-crawler',
    author='Henri-Olivier Duché',
    author_email='hoduche@yahoo.fr',
    license='MIT',
    keywords='fs filesystem files duplicate',
    packages=find_packages(),
    include_package_data=True,
    install_requires=find_requirements(),
    python_requires='>=3',
    entry_points={'console_scripts': ['fs-crawl = fs_crawler.crawl:main']},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
