"""Configuration and helper functions for App Store link verification.

This module contains all helper functions and utilities used by the test suite.
"""

import json
import re
from pathlib import Path


# Global storage for test results
test_results = []

# File paths
BASE_DIR = Path(__file__).parent
DATA_FILE = BASE_DIR / "list_data.json"


def get_app_data():
    """Read URLs from list_data.json and extract app information.
    
    Parses the JSON data file to extract:
    - App group names
    - Original URLs
    - App IDs
    - Constructed test URLs
    
    Returns:
        list: Tuples of (app_group, original_url, new_url, app_id)
    """
    data = []
    
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            app_groups = json.load(f)
        
        for group_name, urls in app_groups.items():
            for url in urls:
                # Extract ID from URL
                id_match = re.search(r'id(\d+)', url)
                
                if id_match:
                    app_id = id_match.group(1)
                    new_url = f"https://apps.apple.com/vn/app/id{app_id}?l=vi"
                    data.append((group_name, url, new_url, app_id))
                else:
                    data.append((group_name, url, None, None))
    except FileNotFoundError:
        pass
    
    return data


def extract_app_name(page):
    """Extract app name from the page.
    
    Args:
        page: Playwright Page object
        
    Returns:
        str: App name or error message
    """
    try:
        app_name_locator = page.locator("h1").first
        if app_name_locator.is_visible():
            return app_name_locator.inner_text().strip()
        return "Not found (h1 hidden)"
    except Exception as e:
        return f"Error extracting ({e})"


def record_test_result(app_group, app_id, status, reason=""):
    """Record test result for reporting.
    
    Args:
        app_group: App group name
        app_id: App ID
        status: Test status ('PASSED' or 'FAILED')
        reason: Failure reason (optional)
    """
    test_results.append({
        'group': app_group,
        'id': app_id,
        'status': status,
        'reason': reason
    })
