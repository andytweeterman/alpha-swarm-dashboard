from playwright.sync_api import sync_playwright
import time
import sys

def verify_ux():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            print("Navigating to app...")
            page.goto("http://localhost:8501", timeout=60000)

            # Wait for app to load - check for header or error
            try:
                page.wait_for_selector(".header-bar", timeout=30000)
                print("Header found.")
            except:
                print("Header not found. Checking for errors...")
                if page.locator("text=Connection Failed").count() > 0:
                    print("ERROR: Connection Failed.")
                elif page.locator("text=Data Feed Unavailable").count() > 0:
                    print("ERROR: Data Feed Unavailable.")
                else:
                    print("Unknown error or timeout.")
                page.screenshot(path="verification/verification_error.png")
                return

            # Wait for market cards
            print("Waiting for market cards...")
            try:
                page.wait_for_selector(".market-card", timeout=30000)
                print("Market cards found.")
            except:
                print("Market cards not found (Data loading failed?).")
                page.screenshot(path="verification/verification_error_cards.png")
                return

            # Check ARIA label
            card = page.locator(".market-card").first
            aria_label = card.get_attribute("aria-label")
            print(f"First Card ARIA Label: {aria_label}")

            if aria_label and ("up" in aria_label or "down" in aria_label):
                print("SUCCESS: ARIA label contains directional text.")
            else:
                print("FAILURE: ARIA label missing or incorrect.")

            # Check role
            role = card.get_attribute("role")
            if role == "group":
                print("SUCCESS: Role is 'group'.")
            else:
                print(f"FAILURE: Role is '{role}', expected 'group'.")

            # Check inner elements hidden
            hidden_elements = card.locator("[aria-hidden='true']")
            count = hidden_elements.count()
            print(f"Found {count} aria-hidden elements inside card.")
            if count >= 3:
                print("SUCCESS: Inner elements are hidden from screen readers.")
            else:
                print("FAILURE: Inner elements not correctly hidden.")

            # Check computed color of delta
            delta = card.locator(".market-delta").first
            color = delta.evaluate("el => window.getComputedStyle(el).color")
            print(f"Delta Color: {color}")
            # We expect resolved RGB values.
            # Light mode green: #007a3d -> rgb(0, 122, 61)
            # Light mode red: #d92b2b -> rgb(217, 43, 43)
            # Dark mode green: #00d26a -> rgb(0, 210, 106)
            # Dark mode red: #f93e3e -> rgb(249, 62, 62)

            # Since default is Light Mode unless toggled
            if "rgb(0, 122, 61)" in color or "rgb(217, 43, 43)" in color:
                 print("SUCCESS: Color matches Light Mode accessible theme.")
            elif "rgb(0, 210, 106)" in color or "rgb(249, 62, 62)" in color:
                 print("WARNING: Color matches Dark Mode theme (is dark mode active?).")
            else:
                 print(f"WARNING: Color {color} does not match expected accessible values.")

            print("Taking screenshot...")
            page.screenshot(path="verification/verification.png", full_page=True)
            print("Screenshot saved to verification/verification.png")

        except Exception as e:
            print(f"Error: {e}")
            page.screenshot(path="verification/verification_exception.png")
        finally:
            browser.close()

if __name__ == "__main__":
    verify_ux()
