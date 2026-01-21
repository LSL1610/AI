from playwright.sync_api import Page
from conftest import analyze_data_source
from data import URL

def test_sjc_gold_price_modular(gold_page, interceptor):
    """
    Modular test to intercept network requests and extract SJC gold prices.
    Uses fixtures from conftest.py and data from data.py.
    """
    # 1. Execution
    gold_page.navigate_and_listen(URL, interceptor)

    # 2. specific API/Source Validation
    matched_response = interceptor.get_matched_response()
    analyze_data_source(matched_response)
    
    # 3. Extraction
    sell_price = gold_page.extract_sjc_sell_price()
    print(f"\nBrand: SJC")
    print(f"Sell Price: {sell_price}")

    # 4. Verification
    assert sell_price, "Price should not be empty"
    assert any(c.isdigit() for c in sell_price), "Price should contain digits"
