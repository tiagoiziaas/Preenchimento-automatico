# preenchimento_app/runner.py
from playwright.sync_api import sync_playwright


def run_automation(url: str, mapping: list[dict], rows: list[dict], delay_ms: int, loop_all: bool, row_index: int, log_cb=None):
    delay = max(0, int(delay_ms))

    if not loop_all:
        idx = int(row_index) - 1
        if idx < 0 or idx >= len(rows):
            raise ValueError("Linha inválida.")
        rows_to_run = [rows[idx]]
    else:
        rows_to_run = rows

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.goto(url, wait_until="domcontentloaded")

        total = len(rows_to_run)
        for i, row in enumerate(rows_to_run, start=1):
            if log_cb:
                log_cb(f"[RUN] Linha {i}/{total}")

            for field in mapping:
                selector = field.get("selector", "")
                action = field.get("action", "fill")
                if not selector:
                    continue

                page.wait_for_selector(selector, state="visible", timeout=15000)

                if action == "click":
                    page.click(selector)
                else:
                    col = field.get("column", "")
                    value = str(row.get(col, "")) if col else ""
                    page.fill(selector, "")
                    page.fill(selector, value)

                if delay:
                    page.wait_for_timeout(delay)

        browser.close()