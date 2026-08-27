import os
import sys

# Add the project root to the Python path so Sphinx can find the package.
sys.path.insert(0, os.path.abspath(".."))

project = "Winery Adventures"
copyright = "2026, Emanuela Cannas, Giada Orrù"
author = "Emanuela Cannas, Giada Orrù"
release = "0.1.2"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = "alabaster"
html_static_path = ["_static"]
