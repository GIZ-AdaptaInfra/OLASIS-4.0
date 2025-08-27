"""Top-level package for the OLASIS 4.0 application.

This package exposes helper functions and classes used throughout the
Flask app and any other back-end. See individual modules for details.
"""

from .chatbot import Chatbot  # noqa: F401 - Compatibilidade
from .chatbot_v2 import OlaBot  # noqa: F401 - Nova implementacao
from .articles import search_articles  # noqa: F401
from .specialists import search_specialists  # noqa: F401
