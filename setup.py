# -*- coding: UTF-8 -*-

import pathlib
import re

from setuptools import setup, find_packages

project_path = pathlib.Path(__file__).parent


def find_readme():
    with open(project_path / 'README.md', encoding='utf-8') as readme_file:
        result = readme_file.read()
        return result


def find_requirements():
    with open(project_path / 'requirements.txt',
              encoding='utf-8') as requirements_file:
        result = [each_line.strip()
                  for each_line in requirements_file.read().splitlines()]
        return result


def find_version():
    with open(project_path / 'alfeios' / '__init__.py',
              encoding='utf-8') as version_file:
        pattern = '^__version__ = [\'\"]([^\'\"]*)[\'\"]'
        match = re.search(pattern, version_file.readline().strip())
        if match:
            result = match.group(1)
            return result


setup(
    name='alfeios',
    version=find_version(),
    description='Enrich your command-line shell with Herculean cleaning'
                ' capabilities',
    long_description=find_readme(),
    long_description_content_type='text/markdown',
    url='https://github.com/hoduche/alfeios',
    download_url='https://github.com/hoduche/alfeios/archive/v0.0.1.tar.gz',
    author='Henri-Olivier Duché',
    author_email='hoduche@yahoo.fr',
    license='MIT',
    keywords='fs filesystem file system walk crawl files duplicate missing'
             ' content hash hashcode checksum zip',
    packages=find_packages(),
    include_package_data=True,
    install_requires=find_requirements(),
    python_requires='>=3.6',
    entry_points={'console_scripts': ['alfeios = alfeios.cli:main']},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
