from playwright.sync_api import sync_playwright
import time

def run(playwright):
    browser = playwright.chromium.launch(headless=True)
    page = browser.new_page()
    try:
        page.goto("http://localhost:8501")
        page.wait_for_selector("text=Enable Dark Mode", timeout=60000)

        # Ensure Dark Mode is ON
        toggle = page.get_by_role("checkbox", name="Enable Dark Mode")
        if not toggle.is_checked():
            print("Dark Mode is OFF. Turning it ON...")
            toggle.check()
            time.sleep(2) # Wait for reload
        else:
            print("Dark Mode is ALREADY ON.")

        # Locate the tooltip icon (Help button)
        help_button = page.get_by_role("button", name="Help for Enable Dark Mode")

        if help_button.is_visible():
            print("Found Help button. Hovering...")
            help_button.hover()
            time.sleep(1) # Wait for tooltip to appear

            # Take a screenshot of the tooltip area (or full page)
            page.screenshot(path="verification/tooltip_dark_mode.png")
            print("Screenshot taken: verification/tooltip_dark_mode.png")

            # Try to print the tooltip content color
            # Streamlit tooltips are usually in a div with role="tooltip" or similar
            tooltip_content = page.locator('div[role="tooltip"]')

            # Also check specific data-testid
            st_tooltip = page.locator('div[data-testid="stTooltipContent"]')
            if st_tooltip.count() > 0:
                print("Found div[data-testid='stTooltipContent']")

            if tooltip_content.is_visible():
                print("Tooltip content is visible.")
                # Get computed style
                color = tooltip_content.evaluate("element => getComputedStyle(element).color")
                bg_color = tooltip_content.evaluate("element => getComputedStyle(element).backgroundColor")
                print(f"Tooltip Text Color: {color}")
                print(f"Tooltip Background Color: {bg_color}")

                # Check children too if color is inherited
                child = tooltip_content.locator("*").first
                if child.is_visible():
                     child_color = child.evaluate("element => getComputedStyle(element).color")
                     print(f"Tooltip Child Text Color: {child_color}")

            else:
                # Try finding by class if role="tooltip" doesn't work
                # Sometimes it's just a div with high z-index
                print("Tooltip content with role='tooltip' NOT visible. Checking other selectors.")
                # Look for a div that appeared recently or is at the end of body
                # This is hard to guess. The screenshot will be key.
        else:
            print("Help button NOT found.")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        browser.close()

with sync_playwright() as playwright:
    run(playwright)
