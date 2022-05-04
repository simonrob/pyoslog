import os
from setuptools import setup, Extension

NAME = 'pyoslog'

about = {}
working_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(working_directory, NAME, '__version__.py')) as version_file:
    exec(version_file.read(), about)

with open('README.md') as readme_file:
    readme = readme_file.read()

# https://setuptools.pypa.io/en/latest/references/keywords.html
setup(
    name=NAME,
    version=about['__version__'],
    description=about['__description__'],
    long_description=readme,
    long_description_content_type='text/markdown',
    author=about['__author__'],
    author_email=about['__author_email__'],
    url=about['__url__'],

    platforms=['darwin'],
    ext_modules=[Extension('_' + NAME, ['%s/_%s.c' % (NAME, NAME)])],

    package_data={'': ['LICENSE']},
    include_package_data=True,

    license=about['__license__'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Operating System :: MacOS',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python'
    ]
)
