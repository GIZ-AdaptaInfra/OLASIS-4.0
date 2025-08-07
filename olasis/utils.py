"""Utility functions for OLASIS 4.0.

This module centralises common helpers such as HTTP requests and data
formatting.  Functions defined here are intentionally simple to avoid
dependencies on the Streamlit framework.
"""
from __future__ import annotations

import json
import logging
from typing import Any, Dict, List, Optional

import requests

logger = logging.getLogger(__name__)


def http_get(url: str, *, headers: Optional[Dict[str, str]] = None,
             params: Optional[Dict[str, Any]] = None,
             timeout: float = 10.0) -> Optional[Dict[str, Any]]:
    """Perform an HTTP GET request and return the parsed JSON response.

    This helper centralises error handling around `requests` so that
    calling modules don't need to catch exceptions repeatedly.  It
    returns the parsed JSON on success or ``None`` on failure.

    Args:
        url: Full URL to request.
        headers: Optional headers to include.  If not provided, a default
            Accept header of ``application/json`` will be used.
        params: URL parameters to encode into the query string.
        timeout: Timeout in seconds for the request (default 10 seconds).

    Returns:
        The decoded JSON response as a dictionary, or ``None`` if the
        request failed or the response could not be decoded.
    """
    final_headers: Dict[str, str] = {'Accept': 'application/json'}
    if headers:
        final_headers.update(headers)

    try:
        resp = requests.get(url, headers=final_headers, params=params, timeout=timeout)
        resp.raise_for_status()
    except Exception as exc:
        logger.error("HTTP request to %s failed: %s", url, exc)
        return None
    try:
        return resp.json()
    except json.JSONDecodeError:
        logger.error("Failed to decode JSON from %s", url)
        return None


def extract_authors(authorships: List[Dict[str, Any]]) -> List[str]:
    """Extract a list of author names from OpenAlex authorship objects.

    Each authorship object is expected to have a ``author`` key with
    ``display_name``.  Authors lacking this field will be ignored.

    Args:
        authorship: List of authorship dictionaries from OpenAlex.

    Returns:
        A list of author display names.
    """
    authors: List[str] = []
    for auth in authorships:
        author = auth.get('author') or {}
        name = author.get('display_name')
        if name:
            authors.append(name)
    return authors
