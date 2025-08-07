"""ORCID integration for specialist search.

This module provides functions to query the ORCID public search API.  The
ORCID FAQ explains that you can search public email addresses and
affiliations using endpoints like ``https://pub.orcid.org/v3.0/search/?q=email:*@orcid.org``
or ``https://pub.orcid.org/v3.0/search/?q=affiliation-org-name:\"ORCID\"``【611596853467428†L25-L40】.
Here we generalise that behaviour: any user‑provided search string is
encoded into the ``q`` parameter.  Results are returned as simplified
dictionaries suitable for display in the Streamlit UI.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from .utils import http_get

ORCID_SEARCH_URL = 'https://pub.orcid.org/v3.0/search/'
ORCID_RECORD_URL_TEMPLATE = 'https://pub.orcid.org/v3.0/{orcid}'


def search_specialists(query: str, *, rows: int = 5) -> List[Dict[str, Any]]:
    """Search for specialists in ORCID using a free‑text query.

    Parameters
    ----------
    query: str
        A Lucene query string.  ORCID supports wildcards and field names such
        as ``email``, ``family-name`` and ``affiliation-org-name``.  If you
        provide a plain name (e.g. "João Pereira") the API will search
        across multiple fields.
    rows: int
        Maximum number of search results to return.  ORCID allows up to 200
        results per request; a smaller number is recommended for speed.  The
        default is 5.

    Returns
    -------
    list of dict
        Each dictionary contains the keys ``orcid``, ``given_names``,
        ``family_names``, ``full_name`` and ``profile_url``.  If an error
        occurs or no results are found, an empty list is returned.
    """
    rows = max(1, min(rows, 200))
    params: Dict[str, Any] = {
        'q': query,
        'rows': rows,
    }
    # Request JSON; ORCID returns XML by default if no Accept header is sent.
    headers = {'Accept': 'application/json'}
    data = http_get(ORCID_SEARCH_URL, headers=headers, params=params)
    if not data or 'result' not in data:
        return []
    
    specialists: List[Dict[str, Any]] = []
    for item in data.get('result', []):
        # Each item contains only 'orcid-identifier', we need to fetch the full record
        orcid_identifier = item.get('orcid-identifier', {})
        path = orcid_identifier.get('path')
        uri = orcid_identifier.get('uri') or f'https://orcid.org/{path}' if path else None
        
        if not path:
            continue
            
        # For performance, try to get names from the summary endpoint first (faster)
        # Only fetch detailed record if we can't get basic info
        given = None
        family = None
        full_name = None
        
        # Try to get basic info from the search result if available
        if 'given-names' in item and item['given-names']:
            given_names = item.get('given-names')
            if given_names and 'value' in given_names:
                given = given_names['value']
                
        if 'family-names' in item and item['family-names']:
            family_names = item.get('family-names')
            if family_names and 'value' in family_names:
                family = family_names['value']
        
        # If we don't have names from search, fetch from record (but limit to avoid slowness)
        if not given and not family and len(specialists) < 10:  # Only fetch details for first 10
            record_url = ORCID_RECORD_URL_TEMPLATE.format(orcid=path)
            record_data = http_get(record_url, headers=headers)
            
            if record_data and 'person' in record_data:
                person = record_data['person']
                if 'name' in person and person['name']:
                    name_info = person['name']
                    given_names = name_info.get('given-names')
                    family_names = name_info.get('family-name')
                    
                    if given_names and 'value' in given_names:
                        given = given_names['value']
                    if family_names and 'value' in family_names:
                        family = family_names['value']
        
        full_name = " ".join(filter(None, [given, family])) or None
        
        # If we couldn't get names, use ORCID ID as fallback
        if not full_name:
            full_name = f"Pesquisador {path[-4:]}"  # Use last 4 digits of ORCID
            
        specialists.append({
            'orcid': path,
            'given_names': given,
            'family_names': family,
            'full_name': full_name,
            'profile_url': uri,
        })
    
    return specialists
