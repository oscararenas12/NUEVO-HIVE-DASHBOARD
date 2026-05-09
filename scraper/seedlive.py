"""
SeedLive Report Scraper

Logs into SeedLive, runs reports, waits for generation, and downloads them as CSV.
Daily Item Export is the primary report (per-transaction, slot-level data).

Usage:
    # Pull yesterday's Daily Item Export (default)
    uv run python -m scraper.seedlive

    # Pull Daily Item Export for a custom date range
    uv run python -m scraper.seedlive --report daily_item --start 04/09/2026 --end 05/09/2026

    # Pull Sales Rollup
    uv run python -m scraper.seedlive --report sales_rollup

    # Pull Detailed Activity
    uv run python -m scraper.seedlive --report detailed_activity

    # Pull Transaction Line Item Export
    uv run python -m scraper.seedlive --report transaction_line_item

    # Show browser while running
    uv run python -m scraper.seedlive --visible
"""

import argparse
import os
import time
from datetime import datetime, timedelta

from dotenv import load_dotenv
from playwright.sync_api import sync_playwright, Page, BrowserContext

load_dotenv()

EMAIL = os.getenv("SEEDLIVE_EMAIL")
PASSWORD = os.getenv("SEEDLIVE_PASSWORD")

URLS = {
    "login": "https://seedlive.com/home.i",
    "home": "https://seedlive.com/home.i?selectedMenuItem=110&profileId=165351",
    "recent_reports": "https://seedlive.com/report_request_history.i?isByProfile=false",
    "report_register": "https://seedlive.com/user_report.i?selectedMenuItem=155&profileId=165351",
    "build_report": "https://seedlive.com/activity_parameters.i?usage=B&selectedTab=10&selectedMenuItem=130&profileId=165351",
}

DOWNLOAD_DIR = os.path.abspath("scraper/downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


# ─── Core ───


def login(page: Page):
    page.goto(URLS["login"], wait_until="networkidle")
    page.fill("input[name='username']", EMAIL)
    page.fill("input[type='password']", PASSWORD)
    page.click("input[type='submit']")
    page.wait_for_load_state("networkidle", timeout=15000)
    time.sleep(2)


def wait_for_ready(page: Page, max_wait=120) -> bool:
    """Poll until all pending reports finish generating."""
    page.goto(URLS["home"], wait_until="networkidle")
    start = time.time()
    last = ""

    while time.time() - start < max_wait:
        page.reload(wait_until="networkidle")
        time.sleep(2)
        try:
            texts = page.eval_on_selector_all(
                "a[href*='report_request_history']",
                "els => els.map(e => e.innerText.trim())"
            )
            current = texts[0] if texts else ""
            if current != last:
                print(f"  [{int(time.time() - start)}s] {current}")
                last = current
            if "Pending (0)" in current:
                return True
        except Exception:
            pass
        time.sleep(5)

    print(f"  Timed out after {max_wait}s")
    return False


def download_latest(page: Page, count=1) -> list[str]:
    """Download the latest N reports from Recent Reports."""
    page.goto(URLS["recent_reports"], wait_until="networkidle")
    time.sleep(2)

    links = page.evaluate("""(count) => {
        const anchors = Array.from(document.querySelectorAll('a[href*="retrieve_report"]'));
        return anchors.slice(0, count).map(a => {
            const row = a.closest('tr');
            const cells = row ? Array.from(row.querySelectorAll('td')) : [];
            return {
                name: cells.length > 0 ? cells[0].innerText.trim() : '',
                href: a.href
            };
        });
    }""", count)

    downloaded = []
    for link in links:
        name = link["name"]
        if not name:
            continue
        page.goto(URLS["recent_reports"], wait_until="networkidle")
        time.sleep(1)
        try:
            req_id = link["href"].split("requestId=")[1].split("&")[0]
            with page.expect_download(timeout=20000) as dl:
                page.click(f"a[href*='requestId={req_id}']")
            download = dl.value
            filename = download.suggested_filename or name
            path = os.path.join(DOWNLOAD_DIR, filename)
            download.save_as(path)
            print(f"  {filename} ({os.path.getsize(path):,} bytes)")
            downloaded.append(path)
        except Exception as e:
            print(f"  Failed: {name} — {str(e)[:60]}")

    return downloaded


# ─── Reports ───
# Each function submits one report. The caller handles waiting + downloading.


def pull_daily_item_export(page: Page, start: str, end: str):
    """Per-transaction, slot-level data. The main report."""
    page.goto(URLS["report_register"], wait_until="networkidle")
    time.sleep(1)
    page.click("text=Daily Item Export (Oscar M Arenas)")
    time.sleep(1)
    page.fill("#startDateId", start)
    page.fill("#endDateId", end)
    page.click("a:has-text('Run Report Sample')")
    page.wait_for_load_state("networkidle", timeout=15000)
    time.sleep(2)


def pull_sales_rollup(page: Page, start: str, end: str):
    """Aggregated totals by device + payment type. CSV format."""
    url = (
        "https://seedlive.com/activity_rollup_parameters.i"
        f"?reportTitle=Sales+Rollup+Report&outputType=27"
        f"&params.beginDate={start}&params.endDate={end}"
    )
    page.goto(url, wait_until="networkidle")
    time.sleep(1)
    page.click("input[name='outputType'][value='21']")
    time.sleep(0.5)
    page.click("input[name='Submit']")
    page.wait_for_load_state("networkidle", timeout=15000)
    time.sleep(2)


def pull_detailed_activity(page: Page, start: str, end: str):
    """Daily totals by device + payment type. CSV format."""
    page.goto(URLS["build_report"], wait_until="networkidle")
    time.sleep(1)
    page.click("a:has-text('detailed report')")
    page.wait_for_load_state("networkidle", timeout=10000)
    time.sleep(1)

    s = datetime.strptime(start, "%m/%d/%Y")
    e = datetime.strptime(end, "%m/%d/%Y")
    page.select_option("#beginMonth", s.strftime("%B"))
    page.select_option("#beginDay", str(s.day))
    page.select_option("#beginYear", str(s.year))
    page.select_option("#endMonth", e.strftime("%B"))
    page.select_option("#endDay", str(e.day))
    page.select_option("#endYear", str(e.year))

    page.click("input[name='outputType'][value='21']")
    time.sleep(0.5)
    page.click("input[value='Run Report']")
    page.wait_for_load_state("networkidle", timeout=15000)
    time.sleep(2)


def pull_transaction_line_item(page: Page, start: str, end: str):
    """Individual transaction line items from Saved Reports."""
    url = (
        "https://seedlive.com/select_date_range_frame_sqlfolio.i"
        "?basicReportId=481&reportTitle=Transaction+Line+Item+Export"
        "&profileId=165351&outputType=21"
    )
    page.goto(url, wait_until="domcontentloaded")
    time.sleep(3)

    # This page may use frames — check for them
    frame = page.main_frame
    for f in page.frames:
        if f != page.main_frame:
            frame = f
            break

    for selector in ["input[name='params.StartDate']", "#startDateId", "input[name='StartDate']"]:
        el = frame.query_selector(selector)
        if el:
            el.fill(start)
            break
    for selector in ["input[name='params.EndDate']", "#endDateId", "input[name='EndDate']"]:
        el = frame.query_selector(selector)
        if el:
            el.fill(end)
            break

    time.sleep(0.5)
    submit = frame.query_selector("input[value='Run Report'], input[name='Submit']")
    if submit:
        submit.click()
        page.wait_for_load_state("domcontentloaded", timeout=30000)
        time.sleep(3)


REPORTS = {
    "daily_item": pull_daily_item_export,
    "sales_rollup": pull_sales_rollup,
    "detailed_activity": pull_detailed_activity,
    "transaction_line_item": pull_transaction_line_item,
}


# ─── Entrypoint ───


def pull_report(report_name: str, start: str, end: str, visible=False) -> list[str]:
    """
    Run a SeedLive report and download the result.
    Returns list of downloaded file paths.

    This is the main function to call from other code (API, UI, etc).
    """
    report_fn = REPORTS.get(report_name)
    if not report_fn:
        raise ValueError(f"Unknown report: {report_name}. Options: {list(REPORTS.keys())}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=not visible, slow_mo=300)
        context = browser.new_context(
            viewport={"width": 1280, "height": 900},
            accept_downloads=True,
        )
        page = context.new_page()

        print(f"Pulling {report_name} ({start} to {end})")
        login(page)
        report_fn(page, start, end)

        print("Waiting for report...")
        wait_for_ready(page)

        print("Downloading...")
        downloaded = download_latest(page, count=1)

        browser.close()

    return downloaded


def main():
    parser = argparse.ArgumentParser(description="Pull reports from SeedLive")
    parser.add_argument("--report", default="daily_item", choices=REPORTS.keys())
    parser.add_argument("--start", default=None, help="Start date MM/DD/YYYY")
    parser.add_argument("--end", default=None, help="End date MM/DD/YYYY")
    parser.add_argument("--visible", action="store_true", help="Show browser")
    args = parser.parse_args()

    today = datetime.now()
    yesterday = today - timedelta(days=1)
    start = args.start or yesterday.strftime("%m/%d/%Y")
    end = args.end or today.strftime("%m/%d/%Y")

    downloaded = pull_report(args.report, start, end, visible=args.visible)

    for path in downloaded:
        lower = path.lower()
        if lower.endswith(".csv") or lower.endswith(".json"):
            print(f"\n{os.path.basename(path)}:")
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                lines = f.read().split("\n")
                for line in lines[:10]:
                    print(f"  {line}")
                if len(lines) > 10:
                    print(f"  ... ({len(lines)} total lines)")


if __name__ == "__main__":
    main()
