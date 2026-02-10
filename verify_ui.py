from playwright.sync_api import sync_playwright
import time

def verify_ui():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        try:
            print("Navigating to app...")
            page.goto("http://localhost:8501")

            # Wait for app to load
            page.wait_for_selector(".glass-header", timeout=20000)

            print("Glass Header found. Checking styles...")
            header = page.locator(".glass-header").first
            bg = header.evaluate("el => window.getComputedStyle(el).backgroundColor")
            print(f"Header Background: {bg}")

            # Light mode default: rgba(0, 0, 0, 0.05)
            # Browsers often return rgba(0, 0, 0, 0.05)
            if "rgba(0, 0, 0, 0.05)" in bg:
                print("SUCCESS: Header background matches expected glass style.")
            else:
                print(f"WARNING: Header background {bg} might not be correct (expected rgba(0, 0, 0, 0.05)).")

            print("Checking Tabs...")
            page.wait_for_selector('button[data-baseweb="tab"]', timeout=10000)
            tab = page.locator('button[data-baseweb="tab"]').first
            tab_bg = tab.evaluate("el => window.getComputedStyle(el).backgroundColor")
            print(f"Tab Background: {tab_bg}")

            if "rgba(0, 0, 0, 0.05)" in tab_bg:
                 print("SUCCESS: Tab background matches expected glass style.")
            else:
                 print(f"WARNING: Tab background {tab_bg} might not be correct.")

            print("Checking Brushed Steel Gradient on H1...")
            # The h1 inside glass-header
            h1 = page.locator(".glass-header h1").first
            h1_bg_img = h1.evaluate("el => window.getComputedStyle(el).backgroundImage")
            print(f"H1 Background Image: {h1_bg_img}")

            if "linear-gradient" in h1_bg_img:
                print("SUCCESS: H1 has a gradient background.")
            else:
                print("WARNING: H1 does not appear to have a gradient background.")

            print("Checking Brushed Steel Gradient on Tab Label...")
            tab_label = page.locator('button[data-baseweb="tab"] div p').first
            # Note: Sometimes p is nested deeper or handled differently.
            # But per CSS selector: button[data-baseweb="tab"] div p
            if tab_label.count() > 0:
                label_bg_img = tab_label.evaluate("el => window.getComputedStyle(el).backgroundImage")
                print(f"Tab Label Background Image: {label_bg_img}")
                if "linear-gradient" in label_bg_img:
                    print("SUCCESS: Tab Label has a gradient background.")
                else:
                    print("WARNING: Tab Label does not appear to have a gradient background.")
            else:
                 print("WARNING: Tab Label selector not found.")

            print("Taking screenshot...")
            page.screenshot(path="verification_screenshot_v3.png", full_page=True)
            print("Screenshot saved to verification_screenshot_v3.png")

        except Exception as e:
            print(f"Error: {e}")
            page.screenshot(path="verification_error_v3.png")
        finally:
            browser.close()

if __name__ == "__main__":
    verify_ui()
