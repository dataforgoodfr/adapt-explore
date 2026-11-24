from pathlib import Path

BOT_NAME = "adaptaville"

SPIDER_MODULES = ["adaptaville"]
NEWSPIDER_MODULE = "adaptaville"

# Identify your crawler
USER_AGENT = "AdaptavilleResearchBot/1.0"

# Respect robots.txt
ROBOTSTXT_OBEY = True

# Request management
DOWNLOAD_DELAY = 2
CONCURRENT_REQUESTS = 4
CONCURRENT_REQUESTS_PER_DOMAIN = 2
DOWNLOAD_TIMEOUT = 30

# Retry handling
RETRY_ENABLED = True
RETRY_TIMES = 3

# Playwright configuration
DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}

TWISTED_REACTOR = (
    "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
)

PLAYWRIGHT_BROWSER_TYPE = "chromium" # Change type if needed

PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT = 30000
PLAYWRIGHT_USE_THREADED_LOOP = False

PLAYWRIGHT_LAUNCH_OPTIONS = {
    "headless": True,
}

# Logging
LOG_LEVEL = "INFO"

# Export retrieve data
BASE_DIR = Path(__file__).resolve().parents[2]

FEEDS = {
    str(BASE_DIR / "data" / "adaptaville.json"): {
        "format": "json",
        "encoding": "utf8",
        "indent": 4,
        "overwrite": True,
    }
}