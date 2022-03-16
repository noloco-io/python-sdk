from setuptools import (
    setup,
    find_packages)


setup(
    name='noloco',
    version='0.3.0',
    description='CRUD operations for Noloco Collections',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Noloco',
    author_email='engineering@noloco.io',
    license='MIT',
    packages=find_packages(exclude=('docs', 'tests')),
    include_package_data=True,
    install_requires=['gql[all]', 'pydash']
)
