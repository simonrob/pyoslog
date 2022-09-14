import os
import sys

import setuptools

NAME = 'pyoslog'

about = {}
working_directory = os.path.join(os.path.abspath(os.path.dirname(__file__)), NAME)
with open(os.path.join(working_directory, '__version__.py')) as version_file:
    exec(version_file.read(), about)

with open('README.md') as readme_file:
    readme = readme_file.read()

# see compatibility.py - allow installation on older versions (or other OSs) but provide is_supported() at runtime
compatibility_module_name = 'compatibility'
compatibility_module_path = os.path.join(working_directory, '%s.py' % compatibility_module_name)
is_old_python_version = sys.version_info < (3, 5,)
try:
    # noinspection PyUnresolvedReferences
    import importlib.util

    if is_old_python_version:  # importlib.util.module_from_spec wasn't always present
        raise ImportError('importlib.util.module_from_spec is not available')
    spec = importlib.util.spec_from_file_location(compatibility_module_name, compatibility_module_path)
    compatibility = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(compatibility)
except ImportError:
    import imp

    compatibility = imp.load_source(compatibility_module_name, compatibility_module_path)

ext_modules = []
# noinspection PyUnresolvedReferences
if compatibility.is_supported():
    ext_modules.append(setuptools.Extension('_' + NAME, ['%s/_%s.c' % (NAME, NAME)]))

# https://setuptools.pypa.io/en/latest/references/keywords.html or https://docs.python.org/3/distutils/apiref.html
setuptools.setup(
    name=NAME,
    version=about['__version__'],
    description=about['__description__'],
    long_description=readme,
    long_description_content_type='text/markdown',
    author=about['__author__'],
    author_email=about['__author_email__'],
    url=about['__url__'],
    project_urls={
        'Documentation': 'https://pyoslog.readthedocs.io/',
        'Bug Tracker': '%s/issues' % about['__url__'],
        'Source Code': about['__url__'],
    },

    platforms=['darwin'],
    packages=[NAME],
    ext_modules=ext_modules,

    # could do, e.g., 'typing;python_version<"3.5"' but some old versions don't support that syntax...
    install_requires=['typing'] if is_old_python_version else [],

    package_data={'': ['LICENSE']},
    include_package_data=True,

    license=about['__license__'],
    classifiers=[
        'Operating System :: MacOS',
        'Programming Language :: Python',
        'Programming Language :: C',
        'Topic :: Software Development',
        'Topic :: System :: Logging',
        'Typing :: Typed',
        'Intended Audience :: Developers',
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: Apache Software License'
    ]
)
