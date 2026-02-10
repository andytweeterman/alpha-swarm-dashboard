from playwright.sync_api import sync_playwright
import time

def verify_ui():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        try:
            print("Navigating to app...")
            page.goto("http://localhost:8501")

            print("Waiting for .glass-header...")
            page.wait_for_selector(".glass-header", timeout=20000)

            print("Glass Header found. Checking styles...")
            header = page.locator(".glass-header").first
            bg = header.evaluate("el => window.getComputedStyle(el).backgroundColor")
            print(f"Header Background: {bg}")
            if "rgba(0, 0, 0, 0.5)" not in bg and "0.5" not in bg:
                print("Warning: Header background might not be correct.")

            print("Checking Tabs...")
            # Wait for tabs
            page.wait_for_selector('button[data-baseweb="tab"]', timeout=10000)
            tab = page.locator('button[data-baseweb="tab"]').first
            tab_bg = tab.evaluate("el => window.getComputedStyle(el).backgroundColor")
            print(f"Tab Background: {tab_bg}")

            print("Checking Settings Button...")
            # Usually the menu button is in header
            menu_btn = page.locator('header button').first
            if menu_btn.count() > 0:
                print("Settings button found.")
                btn_bg = menu_btn.evaluate("el => window.getComputedStyle(el).backgroundColor")
                print(f"Button Background: {btn_bg}")
            else:
                print("Settings button NOT found.")

            print("Taking screenshot...")
            page.screenshot(path="verification_screenshot_v2.png", full_page=True)
            print("Screenshot saved to verification_screenshot_v2.png")

        except Exception as e:
            print(f"Error: {e}")
            page.screenshot(path="verification_error_v2.png")
        finally:
            browser.close()

if __name__ == "__main__":
    verify_ui()
