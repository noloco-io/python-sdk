from setuptools import (
    setup,
    find_packages)


setup(
    name='noloco',
    version='0.1.0',
    description='CRUD operations for Noloco Collections',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Noloco',
    author_email='team@noloco.io',
    license='',  # TODO - write LICENSE
    packages=find_packages(exclude=('docs', 'tests'))
    install_requires=['gql[all]', 'pydash']
)
