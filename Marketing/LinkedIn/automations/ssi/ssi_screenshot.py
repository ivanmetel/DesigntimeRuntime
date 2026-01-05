# screenshot.py
"""
Take LinkedIn SSI screenshot using Playwright with storage state
"""

import os
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

def get_linkedin_storage_state() -> dict:
    """
    Get LinkedIn storage state from environment variable.
    Storage state should be JSON string with cookies and local storage.
    """
    storage_state_json = os.getenv('LINKEDIN_STORAGE_STATE')
    if not storage_state_json:
        raise ValueError("LINKEDIN_STORAGE_STATE not set in env")
    
    return json.loads(storage_state_json)


def take_ssi_screenshot(output_path: str = 'screenshot.png') -> str:
    """
    Take screenshot of LinkedIn SSI page using stored session.
    
    Args:
        output_path: Where to save screenshot
        
    Returns:
        Path to saved screenshot
        
    Raises:
        ValueError: If storage state not available
    """
    
    storage_state = get_linkedin_storage_state()
    
    with sync_playwright() as p:
        browser = p.chromium.launch()
        
        # Create context with stored session
        context = browser.new_context(storage_state=storage_state)
        page = context.new_page()
        
        try:
            # Navigate to SSI page
            page.goto('https://www.linkedin.com/sales/ssi', wait_until='load', timeout=30000)
            
            # Wait for content to load
            page.wait_for_load_state('networkidle', timeout=10000)
            
            # Take screenshot
            page.screenshot(path=output_path, full_page=False)
            
            return output_path
        
        finally:
            context.close()
            browser.close()


if __name__ == '__main__':
    import sys
    try:
        path = take_ssi_screenshot()
        print(f"✅ Screenshot saved: {path}")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)
