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
            print("Waiting for header...")
            try:
                page.wait_for_selector(".header-bar", timeout=30000)
                print("Header found.")
            except:
                print("Header not found.")
                sys.exit(1)

            # Check Header Attributes
            print("Checking Header Attributes...")
            header = page.locator(".header-bar").first
            role = header.get_attribute("role")
            aria_label = header.get_attribute("aria-label")

            if role == "banner":
                print("SUCCESS: Header has role='banner'.")
            else:
                print(f"FAILURE: Header role is '{role}', expected 'banner'.")

            if aria_label == "MacroEffects Dashboard Header":
                print("SUCCESS: Header has correct aria-label.")
            else:
                print(f"FAILURE: Header aria-label is '{aria_label}'.")

            # Check Logo Alt Text
            print("Checking Logo Alt Text...")
            img = header.locator("img").first
            if img.count() > 0:
                alt_text = img.get_attribute("alt")
                if alt_text == "MacroEffects Shield Logo":
                    print("SUCCESS: Logo has correct alt text.")
                else:
                    print(f"FAILURE: Logo alt text is '{alt_text}'.")
            else:
                print("WARNING: Logo image not found (might be missing base64 data).")

            # Check Status Bar
            print("Checking Status Bar...")
            status_bar = page.locator('[role="status"]').first
            if status_bar.count() > 0:
                 print("SUCCESS: Status bar with role='status' found.")
                 sb_label = status_bar.get_attribute("aria-label")
                 if sb_label == "System Status":
                     print("SUCCESS: Status bar has correct aria-label.")
                 else:
                     print(f"FAILURE: Status bar aria-label is '{sb_label}'.")

                 # Check inner pills
                 gov_pill = status_bar.locator(".gov-pill").first
                 if gov_pill.count() > 0:
                     gp_label = gov_pill.get_attribute("aria-label")
                     if gp_label and "Status:" in gp_label:
                         print(f"SUCCESS: Gov Pill has aria-label: {gp_label}")
                     else:
                         print(f"FAILURE: Gov Pill aria-label missing or incorrect: {gp_label}")

                 prem_pill = status_bar.locator(".premium-pill").first
                 if prem_pill.count() > 0:
                     pp_label = prem_pill.get_attribute("aria-label")
                     if pp_label == "Account Status: Premium":
                         print("SUCCESS: Premium Pill has correct aria-label.")
                     else:
                         print(f"FAILURE: Premium Pill aria-label missing or incorrect: {pp_label}")

            else:
                 print("FAILURE: Status bar with role='status' not found.")

            # Scroll to bottom to ensure footer is rendered
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(2)

            # Check Footer
            print("Checking Footer...")
            footer = page.locator('[role="contentinfo"]').first
            if footer.count() > 0:
                print("SUCCESS: Footer with role='contentinfo' found.")
            else:
                print("FAILURE: Footer with role='contentinfo' not found.")
                # Debug: check if text exists
                if page.locator("text=MACROEFFECTS | ALPHA SWARM PROTOCOL").count() > 0:
                     print("DEBUG: Footer text FOUND, but role='contentinfo' selector failed.")
                     # Print the HTML of the footer text container
                     print(page.locator("text=MACROEFFECTS | ALPHA SWARM PROTOCOL").first.evaluate("el => el.outerHTML"))
                     print(page.locator("text=MACROEFFECTS | ALPHA SWARM PROTOCOL").first.evaluate("el => el.parentElement.outerHTML"))
                else:
                     print("DEBUG: Footer text NOT found.")

            print("Taking screenshot...")
            page.screenshot(path="verification/accessibility_check.png", full_page=True)

        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
        finally:
            browser.close()

if __name__ == "__main__":
    verify_accessibility()
