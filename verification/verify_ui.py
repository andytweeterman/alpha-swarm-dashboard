from playwright.sync_api import sync_playwright
import time

def run(playwright):
    browser = playwright.chromium.launch(headless=True)
    page = browser.new_page()
    try:
        page.goto("http://localhost:8501")

        # Wait for either the governance badge OR an error message
        # "GOVERNANCE STATUS" is in the badge
        # "Error loading data" is in the exception block
        try:
            page.wait_for_selector("text=GOVERNANCE STATUS", timeout=60000)
        except:
            print("Timed out waiting for GOVERNANCE STATUS. Checking for errors...")
            if page.locator("text=Error loading data").is_visible():
                print("Error loading data found on page.")
            else:
                print("Unknown state. Taking screenshot.")

        # Take a full page screenshot
        page.screenshot(path="verification/full_page.png", full_page=True)

        # Take a screenshot of the sidebar
        sidebar = page.locator('section[data-testid="stSidebar"]')
        if sidebar.is_visible():
            sidebar.screenshot(path="verification/sidebar.png")

        # Take a screenshot of the premium banner
        banner = page.locator('.premium-banner')
        if banner.is_visible():
            banner.screenshot(path="verification/banner.png")

    except Exception as e:
        print(f"Error: {e}")
        page.screenshot(path="verification/error.png")
    finally:
        browser.close()

with sync_playwright() as playwright:
    run(playwright)
