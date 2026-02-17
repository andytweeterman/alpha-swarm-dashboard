from playwright.sync_api import sync_playwright
import time
import sys

def verify_accessibility():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            print("Navigating to app...")
            page.goto("http://localhost:8501", timeout=60000)

            # Wait for header
            try:
                page.wait_for_selector(".header-bar", timeout=30000)
            except:
                print("Header not found. App might not be loaded.")
                page.screenshot(path="verification/verification_failed_load.png")
                return

            # 1. Check Header Image Alt Text
            # The image is inside .header-bar
            # It might be base64, so selector by src is hard.
            # Select by img tag inside .header-bar
            header_img = page.locator(".header-bar img").first
            alt_text = header_img.get_attribute("alt")
            print(f"Header Image Alt Text: '{alt_text}'")
            if alt_text == "MacroEffects Shield Logo":
                print("SUCCESS: Header image has correct alt text.")
            else:
                print(f"FAILURE: Header image alt text is '{alt_text}', expected 'MacroEffects Shield Logo'.")

            # 2. Check Status Pill Role
            # Selector: .gov-pill
            # Wait for it (might take time for data to load)
            print("Waiting for status pill...")
            try:
                page.wait_for_selector(".gov-pill", timeout=30000)
            except:
                print("Status pill not found (Data loading failed?).")
                page.screenshot(path="verification/verification_failed_pill.png")
                return

            pill = page.locator(".gov-pill").first
            role = pill.get_attribute("role")
            print(f"Status Pill Role: '{role}'")
            if role == "status":
                print("SUCCESS: Status pill has role='status'.")
            else:
                print(f"FAILURE: Status pill role is '{role}', expected 'status'.")

            # 3. Check Status Pill Text Color
            # We need to see if it matches the background contrast.
            # This is dynamic based on status.
            # Let's get the computed style.
            bg_color = pill.evaluate("el => window.getComputedStyle(el).backgroundImage")
            # Note: bg is linear-gradient.
            # Just get color.
            text_color = pill.evaluate("el => window.getComputedStyle(el).color")
            print(f"Status Pill Text Color: {text_color}")

            # If status is "SYSTEM BOOT" (grey), text might be white?
            # If "COMFORT ZONE" (green), text should be BLACK (rgb(0,0,0)).
            # If "CAUTION" (orange), text should be BLACK.
            # If "DEFENSIVE MODE" (red), text should be BLACK.

            status_text = pill.inner_text()
            print(f"Status Text: {status_text}")

            # Check against logic
            if status_text in ["COMFORT ZONE", "CAUTION", "WATCHLIST", "DEFENSIVE MODE"]:
                 if text_color == "rgb(0, 0, 0)":
                     print(f"SUCCESS: {status_text} text is Black.")
                 else:
                     print(f"FAILURE: {status_text} text is {text_color}, expected Black.")
            elif status_text == "SYSTEM BOOT":
                 # Grey background -> White text?
                 # #888888 -> White.
                 if text_color == "rgb(255, 255, 255)":
                     print("SUCCESS: System Boot text is White.")
                 else:
                     print(f"FAILURE: System Boot text is {text_color}, expected White.")
            else:
                 print(f"Unknown Status: {status_text}")

            page.screenshot(path="verification/verification_accessibility.png")
            print("Screenshot saved to verification/verification_accessibility.png")

        except Exception as e:
            print(f"Error: {e}")
            page.screenshot(path="verification/verification_error.png")
        finally:
            browser.close()

if __name__ == "__main__":
    verify_accessibility()
