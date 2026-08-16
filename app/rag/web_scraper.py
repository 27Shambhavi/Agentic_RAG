from __future__ import annotations

import re
from dataclasses import dataclass
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup


# =========================================================
# CONFIG
# =========================================================

REQUEST_TIMEOUT = 20

PLAYWRIGHT_TIMEOUT = 45_000

READER_TIMEOUT = 30

MIN_CONTENT_LENGTH = 100

MAX_SCROLLS = 4

SCROLL_DELAY_MS = 700

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/151.0.0.0 Safari/537.36"
)

HEADERS = {
    "User-Agent": USER_AGENT,

    "Accept": (
        "text/html,"
        "application/xhtml+xml,"
        "application/xml;q=0.9,"
        "image/avif,image/webp,"
        "*/*;q=0.8"
    ),

    "Accept-Language": (
        "en-US,en;q=0.9"
    ),

    "Accept-Encoding": (
        "gzip, deflate, br"
    ),

    "Cache-Control": (
        "no-cache"
    ),

    "Pragma": (
        "no-cache"
    ),

    "Connection": (
        "keep-alive"
    ),
}


# =========================================================
# DATA MODEL
# =========================================================

@dataclass
class ScrapedPage:

    url: str

    title: str

    text: str

    method: str

    status_code: int = 200


# =========================================================
# URL VALIDATION
# =========================================================

def validate_url(
    url: str,
) -> bool:

    url = (
        url or ""
    ).strip()

    if not url:

        return False

    try:

        parsed = urlparse(
            url
        )

    except Exception:

        return False

    return (
        parsed.scheme in {
            "http",
            "https",
        }
        and bool(
            parsed.netloc
        )
    )


# =========================================================
# NORMALIZE URL
# =========================================================

def normalize_url(
    url: str,
) -> str:

    url = (
        url or ""
    ).strip()

    if not url:

        return ""

    if not url.startswith(
        (
            "http://",
            "https://",
        )
    ):

        url = (
            "https://"
            + url
        )

    parsed = urlparse(
        url
    )

    scheme = (
        parsed.scheme.lower()
    )

    netloc = (
        parsed.netloc.lower()
    )

    path = (
        parsed.path.rstrip("/")
    )

    query = (
        parsed.query
    )

    result = (
        f"{scheme}://"
        f"{netloc}"
        f"{path}"
    )

    if query:

        result += (
            f"?{query}"
        )

    return result


# =========================================================
# CLEAN HTML
# =========================================================

def clean_html(
    html: str,
) -> str:

    if not html:

        return ""

    soup = BeautifulSoup(
        html,
        "html.parser",
    )

    # =====================================================
    # REMOVE NON-CONTENT ELEMENTS
    # =====================================================

    for element in soup.find_all(
        [
            "script",
            "style",
            "noscript",
            "svg",
            "canvas",
            "iframe",
            "template",
            "form",
            "button",
            "input",
            "select",
            "textarea",
        ]
    ):

        element.decompose()

    # =====================================================
    # REMOVE NAVIGATION / LAYOUT ELEMENTS
    # =====================================================

    for element in soup.find_all(
        [
            "nav",
            "footer",
            "aside",
        ]
    ):

        element.decompose()

    # =====================================================
    # FIND USEFUL CONTENT
    # =====================================================

    target = (
        soup.find("article")
        or soup.find("main")
    )

    # =====================================================
    # CONTENT-CONTAINER FALLBACK
    # =====================================================

    if not target:

        candidates = soup.find_all(
            "div"
        )

        best_candidate = None

        best_length = 0

        for candidate in candidates:

            classes = " ".join(
                candidate.get(
                    "class",
                    [],
                )
            ).lower()

            candidate_id = (
                candidate.get(
                    "id",
                    "",
                )
                or ""
            ).lower()

            is_content_candidate = any(
                keyword in classes
                or keyword in candidate_id
                for keyword in [
                    "article",
                    "content",
                    "main",
                    "post",
                    "entry",
                    "description",
                    "details",
                    "body",
                    "text",
                ]
            )

            if not is_content_candidate:

                continue

            candidate_text = (
                candidate.get_text(
                    separator="\n",
                    strip=True,
                )
            )

            candidate_length = len(
                candidate_text
            )

            if candidate_length > best_length:

                best_candidate = candidate

                best_length = candidate_length

        target = best_candidate

    # =====================================================
    # BODY FALLBACK
    # =====================================================

    if not target:

        target = (
            soup.body
            if soup.body
            else soup
        )

    # =====================================================
    # EXTRACT TEXT
    # =====================================================

    text = target.get_text(
        separator="\n",
        strip=True,
    )

    # =====================================================
    # NORMALIZE WHITESPACE
    # =====================================================

    lines = []

    for line in text.splitlines():

        line = re.sub(
            r"\s+",
            " ",
            line,
        ).strip()

        if not line:

            continue

        lines.append(
            line
        )

    # =====================================================
    # REMOVE DUPLICATE CONSECUTIVE LINES
    # =====================================================

    cleaned_lines = []

    previous = None

    for line in lines:

        if line == previous:

            continue

        cleaned_lines.append(
            line
        )

        previous = line

    return "\n".join(
        cleaned_lines
    ).strip()


# =========================================================
# CLEAN RENDERED TEXT
# =========================================================

def clean_rendered_text(
    text: str,
) -> str:

    if not text:

        return ""

    lines = []

    for line in text.splitlines():

        line = re.sub(
            r"\s+",
            " ",
            line,
        ).strip()

        if not line:

            continue

        lines.append(
            line
        )

    # =====================================================
    # REMOVE DUPLICATE CONSECUTIVE LINES
    # =====================================================

    cleaned = []

    previous = None

    for line in lines:

        if line == previous:

            continue

        cleaned.append(
            line
        )

        previous = line

    return "\n".join(
        cleaned
    ).strip()


# =========================================================
# EXTRACT TITLE
# =========================================================

def extract_title(
    html: str,
) -> str:

    if not html:

        return "Untitled Webpage"

    try:

        soup = BeautifulSoup(
            html,
            "html.parser",
        )

        # -------------------------------------------------
        # <title>
        # -------------------------------------------------

        title_tag = soup.find(
            "title"
        )

        if title_tag:

            title = title_tag.get_text(
                " ",
                strip=True,
            )

            if title:

                return title

        # -------------------------------------------------
        # <h1>
        # -------------------------------------------------

        heading = soup.find(
            "h1"
        )

        if heading:

            title = heading.get_text(
                " ",
                strip=True,
            )

            if title:

                return title

    except Exception:

        pass

    return "Untitled Webpage"


# =========================================================
# REQUESTS SCRAPER
# =========================================================

def scrape_with_requests(
    url: str,
) -> ScrapedPage:

    print(
        "\n================ WEB SCRAPER ================"
    )

    print(
        "Method: Requests + BeautifulSoup"
    )

    print(
        "URL:",
        url,
    )

    response = requests.get(
        url,
        headers=HEADERS,
        timeout=REQUEST_TIMEOUT,
        allow_redirects=True,
    )

    print(
        "HTTP status:",
        response.status_code,
    )

    print(
        "Final URL:",
        response.url,
    )

    response.raise_for_status()

    # =====================================================
    # CONTENT TYPE
    # =====================================================

    content_type = (
        response.headers.get(
            "content-type",
            "",
        )
        .lower()
    )

    print(
        "Content-Type:",
        content_type,
    )

    if (
        "text/html"
        not in content_type
        and "application/xhtml+xml"
        not in content_type
    ):

        raise ValueError(
            "URL did not return an HTML webpage. "
            f"Content-Type: {content_type}"
        )

    # =====================================================
    # HTML
    # =====================================================

    html = response.text

    print(
        "HTML characters:",
        len(html),
    )

    # =====================================================
    # TITLE
    # =====================================================

    title = extract_title(
        html
    )

    # =====================================================
    # CLEAN CONTENT
    # =====================================================

    text = clean_html(
        html
    )

    print(
        "Extracted text characters:",
        len(text),
    )

    print(
        "Title:",
        title,
    )

    # =====================================================
    # VALIDATE CONTENT
    # =====================================================

    if len(text.strip()) < MIN_CONTENT_LENGTH:

        raise ValueError(
            "The webpage returned too little "
            "meaningful text."
        )

    print(
        "Requests scraping SUCCESS."
    )

    print(
        "=============================================\n"
    )

    return ScrapedPage(
        url=response.url,
        title=title,
        text=text,
        method="requests",
        status_code=response.status_code,
    )


# =========================================================
# PLAYWRIGHT SCRAPER
# =========================================================

def scrape_with_playwright(
    url: str,
) -> ScrapedPage:

    print(
        "\n================ PLAYWRIGHT ================"
    )

    print(
        "URL:",
        url,
    )

    # =====================================================
    # IMPORT
    # =====================================================

    try:

        from playwright.sync_api import (
            sync_playwright,
        )

    except ImportError as error:

        raise RuntimeError(
            "Playwright is not installed.\n\n"
            "Run:\n"
            "pip install playwright\n"
            "playwright install chromium"
        ) from error

    # =====================================================
    # PLAYWRIGHT
    # =====================================================

    with sync_playwright() as p:

        browser = None

        context = None

        try:

            # =================================================
            # BROWSER
            # =================================================

            browser = p.chromium.launch(
                headless=True,
            )

            # =================================================
            # CONTEXT
            # =================================================

            context = browser.new_context(

                user_agent=USER_AGENT,

                locale="en-US",

                viewport={
                    "width": 1440,
                    "height": 900,
                },

                screen={
                    "width": 1440,
                    "height": 900,
                },

                java_script_enabled=True,

                ignore_https_errors=True,

                extra_http_headers={
                    "Accept-Language": (
                        "en-US,en;q=0.9"
                    ),
                },
            )

            # =================================================
            # PAGE
            # =================================================

            page = context.new_page()

            # =================================================
            # BASIC BROWSER NORMALIZATION
            # =================================================

            page.add_init_script(
                """
                Object.defineProperty(
                    navigator,
                    'webdriver',
                    {
                        get: () => undefined
                    }
                );
                """
            )

            # =================================================
            # OPEN PAGE
            # =================================================

            print(
                "[PLAYWRIGHT] Opening page..."
            )

            try:

                page.goto(
                    url,
                    wait_until="domcontentloaded",
                    timeout=PLAYWRIGHT_TIMEOUT,
                )

            except Exception as error:

                print(
                    "[PLAYWRIGHT] Initial navigation "
                    "warning:",
                    repr(error),
                )

                # Page may still contain usable
                # rendered content.

            # =================================================
            # WAIT FOR JAVASCRIPT
            # =================================================

            page.wait_for_timeout(
                3000
            )

            # =================================================
            # WAIT FOR NETWORK IDLE
            # =================================================

            try:

                page.wait_for_load_state(
                    "networkidle",
                    timeout=10_000,
                )

            except Exception:

                print(
                    "[PLAYWRIGHT] Network idle timeout. "
                    "Continuing with rendered page."
                )

            # =================================================
            # COOKIE / CONSENT
            # =================================================

            consent_selectors = [

                "button:has-text('Accept')",

                "button:has-text('I Agree')",

                "button:has-text('Accept All')",

                "button:has-text('Allow all')",

                "[id*='accept']",

                "[class*='accept']",
            ]

            for selector in consent_selectors:

                try:

                    locator = page.locator(
                        selector
                    ).first

                    if locator.is_visible(
                        timeout=1000
                    ):

                        locator.click(
                            timeout=2000
                        )

                        page.wait_for_timeout(
                            1000
                        )

                        break

                except Exception:

                    continue

            # =================================================
            # SCROLL
            # =================================================

            for _ in range(
                MAX_SCROLLS
            ):

                try:

                    page.evaluate(
                        """
                        window.scrollTo(
                            0,
                            document.body.scrollHeight
                        );
                        """
                    )

                    page.wait_for_timeout(
                        SCROLL_DELAY_MS
                    )

                except Exception:

                    break

            # =================================================
            # SCROLL BACK TO TOP
            # =================================================

            try:

                page.evaluate(
                    """
                    window.scrollTo(
                        0,
                        0
                    );
                    """
                )

            except Exception:

                pass

            # =================================================
            # TITLE
            # =================================================

            title = (
                page.title()
                or "Untitled Webpage"
            ).strip()

            # =================================================
            # BODY TEXT
            # =================================================

            try:

                text = page.locator(
                    "body"
                ).inner_text(
                    timeout=15_000
                )

            except Exception:

                text = ""

            text = clean_rendered_text(
                text
            )

            print(
                "Rendered text characters:",
                len(text),
            )

            print(
                "Title:",
                title,
            )

            # =================================================
            # HTML FALLBACK
            # =================================================

            if len(text) < MIN_CONTENT_LENGTH:

                print(
                    "[PLAYWRIGHT] Body text was too short."
                )

                try:

                    html = page.content()

                    text = clean_html(
                        html
                    )

                except Exception as error:

                    print(
                        "[PLAYWRIGHT] HTML fallback failed:",
                        repr(error),
                    )

            # =================================================
            # VALIDATE
            # =================================================

            if len(text) < MIN_CONTENT_LENGTH:

                raise ValueError(
                    "Playwright rendered the page "
                    "but extracted too little text."
                )

            print(
                "Playwright scraping SUCCESS."
            )

            print(
                "Final URL:",
                page.url,
            )

            print(
                "=============================================\n"
            )

            return ScrapedPage(
                url=page.url or url,
                title=title,
                text=text,
                method="playwright",
                status_code=200,
            )

        finally:

            # =================================================
            # CONTEXT CLEANUP
            # =================================================

            if context:

                try:

                    context.close()

                except Exception:

                    pass

            # =================================================
            # BROWSER CLEANUP
            # =================================================

            if browser:

                try:

                    browser.close()

                except Exception:

                    pass


# =========================================================
# GENERIC READER FALLBACK
# =========================================================

def scrape_with_reader(
    url: str,
) -> ScrapedPage:

    """
    Generic fallback for webpages that block normal
    requests or do not expose useful HTML content.

    This is URL-agnostic.

    It is NOT specific to RedBus, Penguin,
    or any other website.
    """

    print(
        "\n================ READER FALLBACK ================"
    )

    print(
        "URL:",
        url,
    )

    # =====================================================
    # JINA READER
    # =====================================================

    reader_url = (
        "https://r.jina.ai/"
        + url
    )

    print(
        "Reader URL:",
        reader_url,
    )

    response = requests.get(
        reader_url,
        headers={
            **HEADERS,

            "Accept": (
                "text/plain,"
                "text/markdown,"
                "*/*;q=0.8"
            ),
        },
        timeout=READER_TIMEOUT,
    )

    print(
        "Reader HTTP status:",
        response.status_code,
    )

    response.raise_for_status()

    # =====================================================
    # TEXT
    # =====================================================

    text = (
        response.text
        or ""
    ).strip()

    text = clean_rendered_text(
        text
    )

    print(
        "Reader extracted characters:",
        len(text),
    )

    # =====================================================
    # VALIDATE
    # =====================================================

    if len(text) < MIN_CONTENT_LENGTH:

        raise ValueError(
            "Reader fallback returned too little "
            "meaningful content."
        )

    # =====================================================
    # TITLE
    # =====================================================

    title = "Untitled Webpage"

    for line in text.splitlines():

        line = line.strip()

        if not line:

            continue

        if line.startswith("#"):

            candidate = (
                line.lstrip("#")
                .strip()
            )

            if candidate:

                title = candidate

                break

    # =====================================================
    # TITLE FALLBACK
    # =====================================================

    if title == "Untitled Webpage":

        first_line = (
            text.splitlines()[0]
            .strip()
        )

        if (
            first_line
            and len(first_line) <= 250
        ):

            title = first_line

    print(
        "Title:",
        title,
    )

    print(
        "Reader fallback SUCCESS."
    )

    print(
        "===================================================\n"
    )

    return ScrapedPage(
        url=url,
        title=title,
        text=text,
        method="reader",
        status_code=response.status_code,
    )


# =========================================================
# MAIN SCRAPER
# =========================================================

def scrape_url(
    url: str,
) -> ScrapedPage:

    # =====================================================
    # NORMALIZE
    # =====================================================

    url = normalize_url(
        url
    )

    # =====================================================
    # VALIDATE
    # =====================================================

    if not validate_url(
        url
    ):

        raise ValueError(
            f"Invalid URL: {url}"
        )

    errors = []

    # =====================================================
    # METHOD 1 — REQUESTS
    # =====================================================

    try:

        return scrape_with_requests(
            url
        )

    except Exception as error:

        errors.append(
            "Requests: "
            + repr(error)
        )

        print(
            "\n[WEB SCRAPER] Requests failed:"
        )

        print(
            repr(error)
        )

    # =====================================================
    # METHOD 2 — PLAYWRIGHT
    # =====================================================

    try:

        return scrape_with_playwright(
            url
        )

    except Exception as error:

        errors.append(
            "Playwright: "
            + repr(error)
        )

        print(
            "\n[WEB SCRAPER] Playwright failed:"
        )

        print(
            repr(error)
        )

    # =====================================================
    # METHOD 3 — GENERIC READER
    # =====================================================

    try:

        return scrape_with_reader(
            url
        )

    except Exception as error:

        errors.append(
            "Reader: "
            + repr(error)
        )

        print(
            "\n[WEB SCRAPER] Reader fallback failed:"
        )

        print(
            repr(error)
        )

    # =====================================================
    # EVERYTHING FAILED
    # =====================================================

    error_message = (
        "Unable to scrape webpage.\n\n"
        + "\n".join(errors)
    )

    print(
        "\n================ SCRAPER FAILED ================"
    )

    print(
        error_message
    )

    print(
        "==================================================\n"
    )

    raise RuntimeError(
        error_message
    )