import os

from setuptools import setup, Extension

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
try:
    # noinspection PyUnresolvedReferences
    import importlib.util

    spec = importlib.util.spec_from_file_location(compatibility_module_name, compatibility_module_path)
    compatibility = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(compatibility)
except ImportError:
    import imp

    compatibility = imp.load_source(compatibility_module_name, compatibility_module_path)

ext_modules = []
if compatibility.is_supported():
    # note: suppress clang warning about pointer to enum cast (and another on version of clang that don't have this...)
    # (warning: cast to smaller integer type 'os_log_type_t' from 'const uint8_t *' (aka 'const unsigned char *'))
    # os_log_type_t *is* uint8_t - see https://opensource.apple.com/source/xnu/xnu-3789.21.4/libkern/os/log.h.auto.html
    ext_modules.append(Extension('_' + NAME, ['%s/_%s.c' % (NAME, NAME)],
                                 extra_compile_args=['-Wno-pointer-to-enum-cast', '-Wno-unknown-warning-option']))

# https://setuptools.pypa.io/en/latest/references/keywords.html
# https://setuptools.pypa.io/en/latest/references/keywords.html or https://docs.python.org/3/distutils/apiref.html
setup(
    name=NAME,
    version=about['__version__'],
    description=about['__description__'],
    long_description=readme,
    long_description_content_type='text/markdown',
    author=about['__author__'],
    author_email=about['__author_email__'],
    url=about['__url__'],
    project_urls={
        'Bug Tracker': '%s/issues' % about['__url__'],
        'Source Code': about['__url__'],
    },

    platforms=['darwin'],
    packages=[NAME],
    ext_modules=ext_modules,

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
