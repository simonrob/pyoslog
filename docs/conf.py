# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import datetime
import os
import sys

# Make sure pyoslog's source files are detected
sys.path.insert(0, os.path.abspath('..'))

# Force-override pyoslog.is_supported() so that we can build the documentation on unsupported platforms
os.environ['PYOSLOG_OVERRIDE_IS_SUPPORTED'] = '1'

# Get properties from __version__.py
about = {}
with open(os.path.join(os.path.abspath('..'), 'pyoslog', '__version__.py')) as version_file:
    exec(version_file.read(), about)

# Import the main README.md
with open(os.path.join(os.path.abspath('.'), 'readme.md'), 'w') as output_file:
    output_file.write("# Overview\n", )
    lines = []
    with open(os.path.join(os.path.abspath('..'), 'README.md')) as readme:
        for line in readme:
            if line.startswith('# '):  # skip main title (we name it 'Overview' above)
                continue
            lines.append(line.rstrip())
    output_file.write('\n'.join(lines))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = about['__title__']

# noinspection PyShadowingBuiltins
copyright = '%d, %s' % (datetime.datetime.now().year, about['__author__'])
author = about['__author__']
version = about['__version__']
release = about['__version__']

print('Documenting', project, version)

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx_toolbox.sidebar_links',
    'sphinx_toolbox.github',
    'recommonmark'  # note: https://github.com/readthedocs/recommonmark/issues/177
]
source_suffix = ['.rst', '.md']

autodoc_member_order = 'bysource'  # note: doesn't work with inherited members: github.com/sphinx-doc/sphinx/issues/628
autodoc_preserve_defaults = True  # better display of log() defaults

github_username = 'simonrob'
github_repository = about['__title__']

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_static_path = ['_static']
html_theme = 'alabaster'
