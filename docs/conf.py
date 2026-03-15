import os
import sys
import django

sys.path.insert(0, os.path.abspath('..'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
django.setup()

# -- Project information ---------------------------------------------------
project = 'News App'
copyright = '2026, Perry Richardson'
author = 'Perry Richardson'
release = '1.0'

# -- General configuration -------------------------------------------------
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output -----------------------------------------------
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']