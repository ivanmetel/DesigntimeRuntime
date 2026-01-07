from playwright.sync_api import sync_playwright
import json
import time

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    
    page.goto('https://www.linkedin.com/login')
    
    print('Login manually in browser...')
    time.sleep(120)  # 2 минуты на логин
    
    state = context.storage_state()
    
    with open('linkedin_state.json', 'w') as f:
        json.dump(state, f)
    
    browser.close()
    print('✅ Storage state saved to linkedin_state.json')
