import pytest
from playwright.sync_api import Page
from data import KNOWN_PRICE_INDICATOR

class GoldDataInterceptor:
    """Class responsible for intercepting and analyzing network requests."""
    
    def __init__(self):
        self.captured_data = {}

    def handle_response(self, response):
        """Callback to process each network response."""
        try:
            content_type = response.headers.get("content-type", "")
            if "image" in content_type or "font" in content_type:
                return

            text = response.text()
            
            # Check for key indicators of gold price data
            if "SJC" in text and "PNJ" in text and KNOWN_PRICE_INDICATOR in text:
                print(f"\n[FOUND] Match in: {response.url} ({response.status})")
                
                if "matched_response" not in self.captured_data:
                    self.captured_data["matched_response"] = {
                        "url": response.url,
                        "body": text,
                        "type": content_type
                    }
        except Exception:
            pass

    def get_matched_response(self):
        return self.captured_data.get("matched_response")


class GoldPricePage:
    """Class responsible for page navigation and DOM extraction."""
    
    def __init__(self, page: Page):
        self.page = page

    def navigate_and_listen(self, url: str, interceptor: GoldDataInterceptor):
        """Navigates to URL while listening to network requests."""
        print(f"Navigating to {url} and listening for API/Docs...")
        self.page.on("response", interceptor.handle_response)
        self.page.goto(url)
        self.page.wait_for_load_state("networkidle")

    def extract_sjc_sell_price(self) -> str:
        """Extracts the SJC sell price from the rendered page."""
        # Locate row with "SJC"
        sjc_row = self.page.locator("tr").filter(
            has=self.page.locator("td strong", has_text="SJC")
        ).first
        
        # Sell price is typically the last 'text-right' cell
        price_cells = sjc_row.locator("td.text-right")
        return price_cells.last.inner_text()


def analyze_data_source(matched_data):
    """Analyzes the intercepted data to determine source type."""
    if not matched_data:
        print("No matching data source found.")
        return

    print(f"Data source identified: {matched_data['url']}")
    
    if "text/html" in matched_data['type']:
        print("Data source is HTML. Parsing content...")
        if matched_data['body'].strip().startswith("{"):
            print("It is distinct JSON API!")
        else:
            print("It is Server-Side Rendered HTML.")

@pytest.fixture
def interceptor():
    return GoldDataInterceptor()

@pytest.fixture
def gold_page(page: Page):
    return GoldPricePage(page)
