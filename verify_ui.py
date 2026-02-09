from playwright.sync_api import sync_playwright
import time

def verify_ui():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        try:
            print("Navigating to app...")
            page.goto("http://localhost:8501")

            # Wait for the main title to ensure the app has loaded
            # Streamlit often loads an initial skeleton, so waiting for specific text is good.
            # Using a timeout of 10s.
            print("Waiting for content...")
            page.wait_for_selector("text=TIEDEMAN RESEARCH", timeout=20000)

            # Wait a bit more for charts to render (Plotly can be slow)
            time.sleep(5)

            print("Taking screenshot...")
            page.screenshot(path="verification_screenshot.png", full_page=True)
            print("Screenshot saved to verification_screenshot.png")

        except Exception as e:
            print(f"Error: {e}")
            # Take a screenshot anyway to see what happened (maybe an error message)
            page.screenshot(path="verification_error.png")
        finally:
            browser.close()

if __name__ == "__main__":
    verify_ui()
