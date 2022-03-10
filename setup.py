from setuptools import (
    setup,
    find_packages)


setup(
    name='Noloco',
    version='0.1.0',
    description='Noloco Python SDK',
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author='Noloco',
    author_email='team@noloco.io',
    license='',  # TODO - write LICENSE
    packages=find_packages(exclude=('docs', 'tests'))
)
