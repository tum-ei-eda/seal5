# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "Seal5"
copyright = "2024, TUM Department of Electrical and Computer Engineering - Chair of Electronic Design Automation"
author = "TUM Department of Electrical and Computer Engineering - Chair of Electronic Design Automation"
release = "v0.1.2"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.viewcode",
    "myst_parser",
    "numpydoc",
    "sphinxemoji.sphinxemoji",
]
numpydoc_show_class_members = False
autosummary_generate = True  # Turn on sphinx.ext.autosummary

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

root_doc = "index"


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# html_theme = 'alabaster'
html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
