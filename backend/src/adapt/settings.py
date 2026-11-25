BOT_NAME = "adapt"

SPIDER_MODULES = ["adapt.spiders"]
NEWSPIDER_MODULE = "adapt.spiders"

USER_AGENT = "AdaptResearchBot/1.0"

ROBOTSTXT_OBEY = True

DOWNLOAD_DELAY = 2
CONCURRENT_REQUESTS = 4
CONCURRENT_REQUESTS_PER_DOMAIN = 2
DOWNLOAD_TIMEOUT = 30

RETRY_ENABLED = True
RETRY_TIMES = 3

DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}

TWISTED_REACTOR = (
    "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
)

PLAYWRIGHT_BROWSER_TYPE = "chromium"

PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT = 30000

PLAYWRIGHT_LAUNCH_OPTIONS = {
    "headless": True,
}

LOG_LEVEL = "INFO"

FEEDS = {
    "data/%(name)s.json": {
        "format": "json",
        "encoding": "utf-8",
        "indent": 4,
        "overwrite": True,
    }
}