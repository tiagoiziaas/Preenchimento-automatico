# preenchimento_app/mapper.py
import json
from playwright.sync_api import sync_playwright

from injected_js import INJECT_JS
from selectors import best_selector


def start_mapping(url: str, on_capture):
    """
    on_capture(payload, selector, label_guess, action)
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        def on_console(msg):
            t = getattr(msg, "text", "")
            text = t if isinstance(t, str) else msg.text()

            if not text.startswith("__MAPPER__"):
                return

            raw = text.replace("__MAPPER__", "", 1)
            try:
                payload = json.loads(raw)
            except Exception:
                return

            if payload.get("ready"):
                on_capture({"ready": True}, "", "", "")
                return

            selector = best_selector(payload)
            label_guess = (
                payload.get("labelText")
                or (payload.get("attrs", {}) or {}).get("placeholder")
                or (payload.get("attrs", {}) or {}).get("name")
                or selector
            )
            action = payload.get("__action", "fill")
            on_capture(payload, selector, label_guess, action)

        page.on("console", on_console)
        page.goto(url, wait_until="domcontentloaded")
        page.evaluate(INJECT_JS)

        page.wait_for_timeout(10_000_000)
        browser.close()
