import os
import time
from playwright.sync_api import sync_playwright

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        try:
            print("Navigating to app...")
            page.goto("http://localhost:8501")

            # Wait for the app to load
            print("Waiting for content...")
            try:
                page.wait_for_selector("text=MacroEffects", timeout=15000)
            except:
                print("Timeout waiting for 'MacroEffects'. Dumping content...")
                print(page.content())
                raise

            # Check Header Image Alt Text
            print("Checking header image alt text...")
            # We look for img with alt="MacroEffects Shield Logo"
            # Since the image is base64, the src is long.
            img = page.locator('img[alt="MacroEffects Shield Logo"]')
            if img.count() > 0:
                print("SUCCESS: Header image has correct alt text.")
            else:
                print("FAILURE: Header image missing alt text.")
                # Debug: print all images
                imgs = page.locator("img").all()
                for i, im in enumerate(imgs):
                    print(f"Image {i} alt: {im.get_attribute('alt')}")

            # Check Status Pill Style
            print("Checking status pill style...")
            # Use a locator for class gov-pill
            # It might take a moment for data to load and pill to appear if it's dependent on data
            # But the app initializes with "SYSTEM BOOT" so it should be there.

            pill = page.locator(".gov-pill").first
            try:
                pill.wait_for(timeout=10000)
                style = pill.get_attribute("style")
                print(f"Status Pill Style: {style}")

                if "color:" in style:
                    print("SUCCESS: Status pill has dynamic color style.")
                else:
                    print("FAILURE: Status pill missing color style.")
            except:
                print("Could not find .gov-pill. Is the app running correctly?")

            # Take screenshot
            os.makedirs("verification", exist_ok=True)
            page.screenshot(path="verification/ux_verification.png")
            print("Screenshot saved to verification/ux_verification.png")

        except Exception as e:
            print(f"Error: {e}")
            page.screenshot(path="verification/error.png")
        finally:
            browser.close()

if __name__ == "__main__":
    run()
