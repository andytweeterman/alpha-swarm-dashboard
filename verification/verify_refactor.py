from playwright.sync_api import sync_playwright
import time

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        try:
            print("Navigating to app...")
            page.goto("http://localhost:8501")

            # Wait for main element
            page.wait_for_selector(".header-bar", timeout=30000)

            print("Found header-bar.")

            # Check market cards
            page.wait_for_selector(".market-card", timeout=10000)
            cards = page.locator(".market-card")
            count = cards.count()
            print(f"Found {count} market cards.")

            if count > 0:
                print("SUCCESS: Market cards rendered.")
            else:
                print("FAILURE: No market cards found.")

            # Take screenshot
            page.screenshot(path="verification/refactor_screenshot.png", full_page=True)
            print("Screenshot saved.")

        except Exception as e:
            print(f"Error: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    run()
