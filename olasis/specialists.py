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


def get_specialist_details(orcid_id: str) -> Dict[str, Any]:
    """Fetch detailed information for a specific ORCID ID.
    
    Parameters
    ----------
    orcid_id : str
        The ORCID identifier (e.g., '0000-0000-0000-0000')
    
    Returns
    -------
    dict
        Dictionary with 'given_names', 'family_names', and 'full_name' keys
    """
    if not orcid_id:
        return {'given_names': None, 'family_names': None, 'full_name': None}
    
    url = ORCID_RECORD_URL_TEMPLATE.format(orcid=orcid_id)
    headers = {'Accept': 'application/json'}
    
    try:
        data = http_get(url, headers=headers)
        if not data or 'person' not in data:
            return {'given_names': None, 'family_names': None, 'full_name': None}
        
        person = data.get('person', {})
        name_info = person.get('name', {})
        
        # Extract given names
        given_names_obj = name_info.get('given-names')
        given = None
        if given_names_obj and given_names_obj.get('value'):
            given = given_names_obj.get('value')
        
        # Extract family names
        family_names_obj = name_info.get('family-name')
        family = None
        if family_names_obj and family_names_obj.get('value'):
            family = family_names_obj.get('value')
        
        # Construct full name
        full_name = " ".join(filter(None, [given, family])).strip() or None
        
        return {
            'given_names': given,
            'family_names': family,
            'full_name': full_name
        }
    except Exception:
        # If any error occurs, return None values
        return {'given_names': None, 'family_names': None, 'full_name': None}


def search_specialists(query: str, *, rows: int = 5, country: str = "") -> List[Dict[str, Any]]:
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
    country: str
        Optional country filter. If provided, adds country filter to the query.

    Returns
    -------
    list of dict
        Each dictionary contains the keys ``orcid``, ``given_names``,
        ``family_names``, ``full_name`` and ``profile_url``.  If an error
        occurs or no results are found, an empty list is returned.
    """
    rows = max(1, min(rows, 200))
    
    # Build query with country filter if provided
    search_query = query
    if country and country.strip():
        search_query = f'({query}) AND (affiliation-org-name:*{country.strip()}* OR address-country:"{country.strip()}")'
    
    params: Dict[str, Any] = {
        'q': search_query,
        'rows': rows,
    }
    # Request JSON; ORCID returns XML by default if no Accept header is sent.
    headers = {'Accept': 'application/json'}
    data = http_get(ORCID_SEARCH_URL, headers=headers, params=params)
    if not data or 'result' not in data:
        return []
    
    # Debug: Print first result to understand structure
    if data.get('result') and len(data.get('result', [])) > 0:
        print("DEBUG - First ORCID result structure:")
        import json
        print(json.dumps(data.get('result')[0], indent=2))
    
    specialists: List[Dict[str, Any]] = []
    for item in data.get('result', []):
        orcid_identifier = item.get('orcid-identifier', {})
        path = orcid_identifier.get('path')
        uri = orcid_identifier.get('uri') or f'https://orcid.org/{path}' if path else None
        
        if not path:
            continue
        
        # Get detailed name information from individual ORCID record
        name_details = get_specialist_details(path)
        given = name_details.get('given_names')
        family = name_details.get('family_names')
        full_name = name_details.get('full_name')
        
        # If we still don't have a name, use fallback
        if not full_name:
            full_name = f"Especialista ORCID: {path}"
        
        specialists.append({
            'orcid': path,
            'given_names': given,
            'family_names': family,
            'full_name': full_name,
            'profile_url': uri,
        })
    return specialists
