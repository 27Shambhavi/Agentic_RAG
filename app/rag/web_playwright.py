from __future__ import annotations

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright


class PlaywrightWebLoader:

    def __init__(
        self,
        timeout: int = 30000,
    ):

        self.timeout = timeout

    def load(
        self,
        url: str,
    ) -> dict:

        with sync_playwright() as playwright:

            browser = playwright.chromium.launch(
                headless=True
            )

            page = browser.new_page()

            page.goto(
                url,
                wait_until="networkidle",
                timeout=self.timeout,
            )

            html = page.content()

            title = page.title()

            browser.close()

        soup = BeautifulSoup(
            html,
            "lxml",
        )

        for tag in soup(
            [
                "script",
                "style",
                "noscript",
                "svg",
                "canvas",
                "iframe",
                "nav",
                "footer",
                "header",
            ]
        ):

            tag.decompose()

        lines = []

        for line in soup.get_text(
            separator="\n"
        ).splitlines():

            line = " ".join(
                line.split()
            )

            if line:

                lines.append(
                    line
                )

        return {
            "url": url,
            "title": title,
            "text": "\n".join(lines),
            "html": html,
            "method": "playwright",
        }


playwright_loader = PlaywrightWebLoader()