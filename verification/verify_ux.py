import time
from playwright.sync_api import sync_playwright

def verify():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            print("Navigating to app...")
            page.goto("http://localhost:8501")

            # Wait for the app to load (Streamlit often takes a moment)
            print("Waiting for app to load...")
            # Wait for the main title to appear. Streamlit apps often have a loading screen.
            # Using wait_for_selector on a specific element
            try:
                page.wait_for_selector(".steel-text-main", timeout=20000)
            except Exception as e:
                print("Timed out waiting for .steel-text-main. Check if app is running.")
                page.screenshot(path="verification/timeout.png")
                return

            # Check Logo Alt Text
            print("Checking Logo accessibility...")
            try:
                # The logo is inside .header-bar
                header_logo = page.locator(".header-bar img").first
                alt_text = header_logo.get_attribute("alt")
                print(f"Logo alt text: {alt_text}")
                if alt_text != "MacroEffects Shield Logo":
                    print(f"FAILURE: Expected alt='MacroEffects Shield Logo', got '{alt_text}'")
                else:
                    print("SUCCESS: Logo alt text correct.")
            except Exception as e:
                print(f"Error checking logo: {e}")

            # Check Market Cards
            print("Checking Market Cards accessibility...")
            # Wait for market cards to load (they depend on data fetching)
            try:
                page.wait_for_selector(".market-card", timeout=10000)
            except:
                print("Market cards not found. Maybe data loading failed?")
                page.screenshot(path="verification/no_cards.png")
                return

            market_cards = page.locator(".market-card")
            count = market_cards.count()
            print(f"Found {count} market cards.")

            if count > 0:
                first_card = market_cards.first
                role = first_card.get_attribute("role")
                aria_label = first_card.get_attribute("aria-label")

                print(f"First card role: {role}")
                print(f"First card aria-label: {aria_label}")

                if role == "group":
                    print("SUCCESS: Role is 'group'")
                else:
                    print(f"FAILURE: Expected role='group', got '{role}'")

                if aria_label and "Market Data" in aria_label:
                    print("SUCCESS: Aria-label contains 'Market Data'")
                else:
                    print(f"FAILURE: Expected aria-label to contain 'Market Data', got '{aria_label}'")

            # Take screenshot
            print("Taking screenshot...")
            page.screenshot(path="verification/ux_verification.png")
            print("Verification complete!")

        except Exception as e:
            print(f"Verification script failed: {e}")
            page.screenshot(path="verification/failure.png")
        finally:
            browser.close()

if __name__ == "__main__":
    verify()
