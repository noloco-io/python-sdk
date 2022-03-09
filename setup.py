from setuptools import (
    setup,
    find_packages)


setup(
    name='Noloco',
    version='0.1.0',
    description='Noloco Python SDK',
    long_description='',  # TODO - write downstream-friendly README
    author='Noloco',
    author_email='team@noloco.io',
    url='https://github.com/noloco/python-sdk',
    license='',  # TODO - write LICENSE
    packages=find_packages(exclude=('docs', 'tests'))
)
