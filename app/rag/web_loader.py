from __future__ import annotations

from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup


@dataclass
class WebPage:

    url: str
    title: str
    text: str
    html: str
    method: str


class WebLoader:

    def __init__(
        self,
        timeout: int = 20,
    ):

        self.timeout = timeout

        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 "
                "(Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/151.0.0.0 Safari/537.36"
            )
        }

    # =====================================================
    # STATIC WEBPAGE
    # =====================================================

    def load(
        self,
        url: str,
    ) -> WebPage:

        response = requests.get(
            url,
            headers=self.headers,
            timeout=self.timeout,
        )

        response.raise_for_status()

        soup = BeautifulSoup(
            response.text,
            "lxml",
        )

        title = ""

        if soup.title:

            title = soup.title.get_text(
                strip=True
            )

        text = self.extract_text(
            soup
        )

        return WebPage(
            url=url,
            title=title,
            text=text,
            html=response.text,
            method="requests+beautifulsoup",
        )

    # =====================================================
    # CLEAN HTML
    # =====================================================

    @staticmethod
    def extract_text(
        soup: BeautifulSoup,
    ) -> str:

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

        return "\n".join(
            lines
        )


web_loader = WebLoader()