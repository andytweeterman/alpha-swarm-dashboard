from playwright.sync_api import sync_playwright
import time

def run(playwright):
    browser = playwright.chromium.launch()
    page = browser.new_page()
    try:
        page.goto("http://localhost:8501")
        page.wait_for_selector(".stApp", timeout=60000)

        # Verify Tab 1: Market Swarm (Default)
        # Market cards are in Tab 1
        page.wait_for_selector(".market-card", state="visible", timeout=30000)

        # Take screenshot of first market card
        card = page.locator(".market-card").first
        card.screenshot(path="verification/market_card_tab1.png")

        # Switch to Tab 2: Risk Governance
        # The tab name might contain emoji, so using loose matching or role
        # Try finding by text inside button
        page.get_by_role("tab", name="Risk Governance").click()

        # Wait for Tab 2 content to be visible
        page.wait_for_selector(".big-badge", state="visible", timeout=30000)

        # Take screenshot of the badge
        badge = page.locator(".big-badge")
        badge.screenshot(path="verification/badge_tab2.png")

        # Take full page screenshot
        page.screenshot(path="verification/full_page.png", full_page=True)

    except Exception as e:
        print(f"Error during verification: {e}")
        page.screenshot(path="verification/error_screenshot.png")
    finally:
        browser.close()

if __name__ == "__main__":
    with sync_playwright() as p:
        run(p)
