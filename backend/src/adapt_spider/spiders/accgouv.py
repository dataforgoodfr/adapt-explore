import scrapy

from scrapy import signals
from scrapy_playwright.page import PageMethod

from rich.progress import (
    Progress,
    SpinnerColumn,
    BarColumn,
    TextColumn,
    TaskProgressColumn,
    TimeElapsedColumn,
)

from adapt_spider.items.initiative import InitiativeItem
from adapt_spider.processors.accgouv import ACCGouvProcessor

class ACCGouvSpider(scrapy.Spider):
    name = "accgouv"
    allowed_domains = ["www.adaptation-changement-climatique.gouv.fr"]
    start_urls = ["https://www.adaptation-changement-climatique.gouv.fr/projets-locaux-financements/localisation#paragraph--21879"]

    def __init__(self, *args, **kwargs):

        # Initialise Driver
        super().__init__(*args, **kwargs)

        self.processor = ACCGouvProcessor(logger=self.logger)
        self.progress = None
        self.progress_task = None

    # =============================
    # Rich Progress
    # =============================
    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super().from_crawler(crawler, *args, **kwargs)

        spider.progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeElapsedColumn(),
        )

        crawler.signals.connect(
            spider.spider_closed,
            signal=signals.spider_closed,
        )

        return spider

    # =============================
    # Load the Leaflet map
    # =============================
    async def start(self):

        for url in self.start_urls:

            yield scrapy.Request(
                url=url,
                callback=self.parse_map, # collect data from map, change this to make a generalisation
                errback=self.check_access,
                # Playwright is needed to access Javascript items in webpage
                meta={
                    "playwright": True,
                    "playwright_page_methods": [
                        PageMethod(
                                "wait_for_selector",
                                ".geolocation-location[data-lat][data-lng]",
                                state="attached", # present in DOM even if hidden
                                timeout=50000,
                        ),
                        PageMethod(
                            "evaluate",
                            """(() => {
                                // Get all geographical records
                                const elements = document.querySelectorAll(
                                    ".geolocation-location[data-lat][data-lng]"
                                );

                                const markers = [...elements].map((el, index) => {
                                    const url = el.querySelector(".location-content a[href]"); 

                                    const name =
                                        el.querySelector(".location-title")
                                            ?.textContent.trim()
                                        || link?.textContent.trim()
                                        || null;

                                    return {
                                        nom: name,
                                        lat: Number(el.dataset.lat),
                                        lng: Number(el.dataset.lng),
                                        url: url
                                            ? new URL(url.getAttribute("href"), document.baseURI).href
                                            : null
                                    };
                                });

                                return markers;
                            })();
                        """
                        ),
                    ],
                }
            )

    def check_access(self, response):

        self.logger.info("=" * 60)
        self.logger.info("HTTP STATUS: %s", response.status)
        self.logger.info("FINAL URL: %s", response.url)
        self.logger.info(
            "CONTENT TYPE: %s",
            response.headers.get("Content-Type"),
        )

        body = response.text.lower()

        indicators = [
            "access denied",
            "captcha",
            "verify you are human",
            "cloudflare",
            "unusual traffic",
            "request blocked",
            "forbidden",
            "security check",
        ]

        for indicator in indicators:
            if indicator in body:
                self.logger.warning(
                    "Possible blocking indicator detected: %s",
                    indicator,
                )

        self.logger.info("PAGE TITLE: %s", response.css("title::text").get())
        self.logger.info("HTML PREVIEW: %s", response.text[:1500])
        self.logger.info("=" * 60)

    # =============================
    # Extract Leaflet markers
    # =============================
    def parse_map(self, response):
        page_methods = response.meta["playwright_page_methods"]
        markers = page_methods[1].result

        self.logger.info(f"Extracted {len(markers)} markers from map")

        # Initialize Rich progress
        self.progress.start()

        self.progress_task = self.progress.add_task(
            "Scraping ACCGouv",
            total=len(markers),
        )

        for marker in markers:
            url = marker.get("url")
            if not url:
                continue

            yield scrapy.Request(
                url=url,
                callback=self.parse_detail,
                errback=self.handle_error,
                cb_kwargs={"marker": marker},
                meta={"playwright": True},
            )

    # =============================
    # Extract information from each page 
    # using `processor`
    # =============================
    def parse_detail(self, response, marker):
        try:
            extracted_data = self.processor.process(response.text)

            item = InitiativeItem()

            item["nom"] = marker.get("nom")
            item["lat"] = marker.get("lat")
            item["lng"] = marker.get("lng")

            item["type_initiative"] = extracted_data.get("type_initiative")
            item["description"] = extracted_data.get("description")
            item["url"] = extracted_data.get("url") or marker.get("url")
            item["image_url"] = extracted_data.get("image_url")
            item["aleas"] = extracted_data.get("aleas")
            item["porteurs"] = extracted_data.get("porteurs")
            # item["porteurs_laya_choice"] = extracted_data.get("porteurs_laya_choice")
            # item["porteurs_laya_proba"] = extracted_data.get("porteurs_laya_proba")
            
            item["localisation"] = extracted_data.get("localisation") or marker.get("localisation")
            item["email"] = extracted_data.get("email") 
            item["contact"] = extracted_data.get("contact")
            
            item["page_text"] = extracted_data.get("page_text")

            item["scraping_status"] = "success"
            item["scraping_error"] = None

            yield item

        except Exception as exc:
            self.logger.exception(
                f"Error processing detail page: {response.url}"
            )

            yield self.build_failed_item(
                response.url,
                marker,
                str(exc),
            )

        finally:
            self.advance_progress()

    def handle_error(self, failure):
        request = failure.request
        marker = request.cb_kwargs.get("marker", {})

        self.logger.error(
            f"Failed to scrape {request.url}: {failure.value}"
        )

        yield self.build_failed_item(
            request.url,
            marker,
            str(failure.value),
        )

        self.advance_progress()

    def build_failed_item(self, url, marker, error):
        item = InitiativeItem()

        item["nom"] = marker.get("nom")
        item["url"] = url
        item["lat"] = marker.get("lat")
        item["lng"] = marker.get("lng")

        item["scraping_status"] = "failed"
        item["scraping_error"] = error

        return item

    def advance_progress(self):
        if self.progress_task is not None:
            self.progress.advance(self.progress_task)

    def spider_closed(self, spider, reason):
        if self.progress is not None:
            self.progress.stop()