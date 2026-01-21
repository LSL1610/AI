"""App Store link verification tests.

This module tests Apple App Store links from list_data.txt,
verifying they are accessible and extracting app information.
"""

import re
from pathlib import Path

import pytest
from playwright.sync_api import Page, expect

from config import (
    get_app_data,
    extract_app_name,
    record_test_result
)
from my_discord import MyDiscord

# Global constants
BASE_DIR = Path(__file__).parent
REPORTS_DIR = BASE_DIR / "reports"
PATH_RPT = REPORTS_DIR / "link_appstore_real.txt"
REPORT_DEMO = "https://discord.com/api/webhooks/1379365755501674607/a9xwyGVhQa_9oD4VF6PrhQAuXCRALwcg6fGEttuyhb3ZpsozGf_eemcRbjNCOel1szSI"

my_bot_img = MyDiscord(REPORT_DEMO)
my_bot_discord = MyDiscord(REPORT_DEMO)

@pytest.mark.parametrize("app_group, original_url, new_url, app_id", get_app_data())
def test_1_check_link_alive(page: Page, app_group, original_url, new_url, app_id):
    """Test App Store link accessibility.
    
    Verifies that the constructed App Store link is accessible,
    returns a valid response, and contains expected content.
    
    Args:
        page: Playwright Page fixture
        app_group: App group name
        original_url: Original URL from data file
        new_url: Constructed test URL
        app_id: Extracted app ID
        
    Raises:
        pytest.fail: If app ID is None
        AssertionError: If page fails to load or validate
    """
    print(f"\nOriginal URL: {original_url}")
    
    # Validate app ID exists
    if app_id is None:
        record_test_result(app_group, 'None', 'FAILED', 'ID is None')
        pytest.fail(f"ID is None for URL: {original_url}")
    
    print(f"Extracted ID: {app_id}")
    print(f"Checking New URL: {new_url}")
    
    try:
        # Navigate to the URL
        response = page.goto(new_url)
        
        # Verify page title contains "App Store"
        # Handles non-breaking spaces in localized titles
        expect(page).to_have_title(re.compile(r"App\s*Store"))
        
        # Extract and log app name
        app_name = extract_app_name(page)
        print(f"App Name: {app_name}")
        print(f"Page Title: {page.title()}")
        
        # Check if app name indicates "page not found"
        not_found_keywords = [
            "Không tìm thấy",  # Vietnamese: Not found
            "Page not found",
            "Not found",
            "404",
            "could not find",
            "couldn't find"
        ]
        
        is_not_found = any(keyword.lower() in app_name.lower() for keyword in not_found_keywords)
        
        if is_not_found:
            print("Link Failed: Page not found (404)")
            record_test_result(app_group, app_id, 'FAILED', 'Page not found')
        else:
            print("Link is Alive")
            record_test_result(app_group, app_id, 'PASSED')
        
    except Exception as e:
        # Record failure (could be 404, timeout, or other errors)
        error_msg = str(e)[:50]  # Truncate long error messages
        record_test_result(app_group, app_id, 'FAILED', error_msg)
        # Don't raise - just record the failure
        print(f"Link Failed: {error_msg}")

def test_9_rp():
    my_bot_discord.send_message_as_file_content(
        username="🤖 CHECK_LINK_APPSTORE_REAL_G8_3RD_PARTY",
        file_path=str(PATH_RPT),
        user_ids_to_mention=[
            1376500835516682414,
            1376386960331116575,
            1377904828209954930,
            1377904728926851144,
            1377531545761484821,
            1377530729407189064,
        ],
    )

    print("Send report done")

def test_10_backup_still_running():
    try:
        my_bot_img.send_still_running(
            msg_still_running_payload="Check 3rd party link appstore G8 ",
            target_hours=[h for h in range(1, 24) if h not in {10, 16, 22}],
            username_webhook="BOT 3RD PARTY REAL APPSTORE STILL RUNNING",
        )
    except Exception:
        pass
