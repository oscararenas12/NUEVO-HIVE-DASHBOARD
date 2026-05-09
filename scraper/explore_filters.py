"""
SeedLive Filter Explorer — Maps out all form fields, dropdowns, and filter
options on each report page. Saves screenshots for reference.

Usage:
    uv run python -m scraper.explore_filters
"""

import os
import time

from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

load_dotenv()

EMAIL = os.getenv("SEEDLIVE_EMAIL")
PASSWORD = os.getenv("SEEDLIVE_PASSWORD")
LOGIN_URL = "https://seedlive.com/home.i"

SCREENSHOT_DIR = "scraper/screenshots/filters"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)


def login(page):
    page.goto(LOGIN_URL, wait_until="networkidle")
    page.fill("input[name='username']", EMAIL)
    page.fill("input[type='password']", PASSWORD)
    page.click("input[type='submit']")
    page.wait_for_load_state("networkidle", timeout=15000)
    time.sleep(2)
    print("Logged in.\n")


def describe_form(page, name):
    """Describe every form element on the current page."""
    print(f"\n{'='*70}")
    print(f"  {name}")
    print(f"  URL: {page.url}")
    print(f"{'='*70}")

    # Text/date inputs
    inputs = page.evaluate("""() => {
        return Array.from(document.querySelectorAll(
            'input:not([type="hidden"]):not([type="submit"]):not([type="button"])'
        )).filter(el => {
            const style = window.getComputedStyle(el);
            return style.display !== 'none' && style.visibility !== 'hidden' && el.offsetParent !== null;
        }).map(i => ({
            type: i.type, name: i.name, id: i.id, value: i.value,
            placeholder: i.placeholder,
            checked: i.checked,
            label: i.parentElement ? i.parentElement.innerText.trim().substring(0, 50) : ''
        }));
    }""")

    if inputs:
        print(f"\n  INPUT FIELDS ({len(inputs)}):")
        for inp in inputs:
            checked = " [CHECKED]" if inp.get('checked') else ""
            val = f" = \"{inp['value']}\"" if inp['value'] else ""
            label = f" -- {inp['label']}" if inp['label'] and inp['label'] != inp['value'] else ""
            print(f"    <{inp['type']}> name={inp['name']} id={inp['id']}{val}{checked}{label}")

    # Dropdowns with all options
    selects = page.evaluate("""() => {
        return Array.from(document.querySelectorAll('select')).filter(el => {
            const style = window.getComputedStyle(el);
            return style.display !== 'none' && style.visibility !== 'hidden' && el.offsetParent !== null;
        }).map(s => ({
            name: s.name, id: s.id,
            selected: s.options[s.selectedIndex] ? s.options[s.selectedIndex].text.trim() : '',
            selectedValue: s.value,
            options: Array.from(s.options).map(o => ({text: o.text.trim(), value: o.value}))
        }));
    }""")

    if selects:
        print(f"\n  DROPDOWNS ({len(selects)}):")
        for sel in selects:
            print(f"    [{sel['id'] or sel['name']}] selected: \"{sel['selected']}\" (value={sel['selectedValue']})")
            for opt in sel['options']:
                marker = "  >>>" if opt['value'] == sel['selectedValue'] else "     "
                print(f"    {marker} \"{opt['text']}\" (value={opt['value']})")

    # Buttons
    buttons = page.evaluate("""() => {
        return Array.from(document.querySelectorAll(
            'input[type="submit"], input[type="button"], button, a'
        )).filter(el => {
            const style = window.getComputedStyle(el);
            const text = (el.value || el.innerText || '').trim();
            return style.display !== 'none' && style.visibility !== 'hidden'
                && el.offsetParent !== null && text.length > 0 && text.length < 40
                && (text.includes('Run') || text.includes('Submit') || text.includes('Search')
                    || text.includes('Report') || text.includes('Export') || text.includes('Save')
                    || text.includes('Sample') || text.includes('Download'));
        }).map(b => ({
            tag: b.tagName, text: (b.value || b.innerText || '').trim(),
            id: b.id, name: b.name, href: b.href || ''
        }));
    }""")

    if buttons:
        print(f"\n  ACTION BUTTONS ({len(buttons)}):")
        for btn in buttons:
            print(f"    <{btn['tag'].lower()}> \"{btn['text']}\" id={btn['id']} name={btn['name']}")

    # Checkboxes grouped by name
    checkboxes = page.evaluate("""() => {
        const groups = {};
        document.querySelectorAll('input[type="checkbox"]').forEach(cb => {
            const style = window.getComputedStyle(cb);
            if (style.display === 'none' || style.visibility === 'hidden' || !cb.offsetParent) return;
            const key = cb.name || cb.id || 'unnamed';
            if (!groups[key]) groups[key] = [];
            const label = cb.parentElement ? cb.parentElement.innerText.trim().substring(0, 60) : '';
            groups[key].push({value: cb.value, checked: cb.checked, label: label, id: cb.id});
        });
        return groups;
    }""")

    if checkboxes:
        print(f"\n  CHECKBOXES:")
        for group_name, cbs in checkboxes.items():
            print(f"    [{group_name}]")
            for cb in cbs:
                checked = "[x]" if cb['checked'] else "[ ]"
                print(f"      {checked} value={cb['value']} -- {cb['label']}")

    # Radio buttons grouped by name
    radios = page.evaluate("""() => {
        const groups = {};
        document.querySelectorAll('input[type="radio"]').forEach(r => {
            const style = window.getComputedStyle(r);
            if (style.display === 'none' || style.visibility === 'hidden' || !r.offsetParent) return;
            const key = r.name || 'unnamed';
            if (!groups[key]) groups[key] = [];
            const label = r.parentElement ? r.parentElement.innerText.trim().substring(0, 60) : '';
            groups[key].push({value: r.value, checked: r.checked, label: label});
        });
        return groups;
    }""")

    if radios:
        print(f"\n  RADIO BUTTONS:")
        for group_name, rds in radios.items():
            print(f"    [{group_name}]")
            for r in rds:
                selected = "(o)" if r['checked'] else "( )"
                print(f"      {selected} value={r['value']} -- {r['label']}")

    print()


def explore_page(page, url, name):
    """Navigate to a page, screenshot it, and describe all form elements."""
    print(f"\n>>> Navigating to {name}...")
    page.goto(url, wait_until="networkidle")
    time.sleep(2)
    page.screenshot(path=f"{SCREENSHOT_DIR}/{name}.png", full_page=True)
    print(f"  Screenshot: {SCREENSHOT_DIR}/{name}.png")
    describe_form(page, name)


def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=300)
        context = browser.new_context(viewport={"width": 1280, "height": 900})
        page = context.new_page()

        login(page)

        # 1. Report Register — Daily Item Export
        print("\n>>> Report Register: selecting Daily Item Export...")
        page.goto("https://seedlive.com/user_report.i?selectedMenuItem=155&profileId=165351",
                  wait_until="networkidle")
        time.sleep(1)
        page.click("text=Daily Item Export (Oscar M Arenas)")
        time.sleep(1)
        page.screenshot(path=f"{SCREENSHOT_DIR}/report_register_daily_item.png", full_page=True)
        describe_form(page, "Report Register: Daily Item Export")

        # 2. Sales Rollup Report form
        explore_page(
            page,
            "https://seedlive.com/activity_rollup_parameters.i?reportTitle=Sales+Rollup+Report&outputType=27",
            "sales_rollup_form"
        )

        # 3. Build a Report — Simple
        explore_page(
            page,
            "https://seedlive.com/activity_parameters.i?usage=B&selectedTab=10&selectedMenuItem=130&profileId=165351",
            "build_report_simple"
        )

        # 4. Build a Report — Detailed
        page.goto("https://seedlive.com/activity_parameters.i?usage=B&selectedTab=10&selectedMenuItem=130&profileId=165351",
                  wait_until="networkidle")
        time.sleep(1)
        page.click("a:has-text('detailed report')")
        page.wait_for_load_state("networkidle", timeout=10000)
        time.sleep(1)
        page.screenshot(path=f"{SCREENSHOT_DIR}/build_report_detailed.png", full_page=True)
        describe_form(page, "Build a Report: Detailed")

        # 5. Build a Report — Sales Rollup tab
        page.goto("https://seedlive.com/activity_parameters.i?usage=B&selectedTab=10&selectedMenuItem=130&profileId=165351",
                  wait_until="networkidle")
        time.sleep(1)
        page.click("a:has-text('sales rollup report')")
        page.wait_for_load_state("networkidle", timeout=10000)
        time.sleep(1)
        page.screenshot(path=f"{SCREENSHOT_DIR}/build_report_sales_rollup.png", full_page=True)
        describe_form(page, "Build a Report: Sales Rollup")

        # 6. Transaction Line Item Export
        explore_page(
            page,
            "https://seedlive.com/select_date_range_frame_sqlfolio.i?basicReportId=481&reportTitle=Transaction+Line+Item+Export&profileId=165351&outputType=21",
            "transaction_line_item_form"
        )

        # 7. Dex Status form
        explore_page(
            page,
            "https://seedlive.com/dex_status_parameters.i?selectedMenuItem=33876&profileId=165351",
            "dex_status_form"
        )

        # 8. Diagnostics form
        explore_page(
            page,
            "https://seedlive.com/diagnostic_parameters.i?selectedMenuItem=135&profileId=165351",
            "diagnostics_form"
        )

        print("\n" + "="*70)
        print("EXPLORATION COMPLETE")
        print(f"Screenshots saved in {SCREENSHOT_DIR}/")
        print("="*70)
        input("\nPress Enter to close browser...")
        browser.close()


if __name__ == "__main__":
    run()
