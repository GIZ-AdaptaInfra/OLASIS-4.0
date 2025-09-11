# C:\Users\darla\OLASIS4.0\olasis\__init__.py
"""OLASIS 4.0 package – exporta a versão anti-intro por padrão."""

from .chatbot import Chatbot  # nossa implementação com filtros anti-intro
OlaBot = Chatbot              # <— garante que "from olasis import OlaBot" use Chatbot

from .articles import search_articles  # noqa: F401
from .specialists import search_specialists  # noqa: F401
