
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

from adaptaville.items import AdaptavilleItem
from adaptaville.processing import HTMLProcessor

class AdaptavilleSpider(scrapy.Spider):
    name = "adaptaville"
    allowed_domains = ["adaptaville.fr"]
    start_urls = ["https://www.adaptaville.fr/carte"]

    def __init__(self, *args, **kwargs):

        # Initialise Driver
        super().__init__(*args, **kwargs)

        self.processor = HTMLProcessor()
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
                errback=self.handle_error,
                # Playwright is needed to access Javascript items in webpage
                meta={
                    "playwright": True,
                    "playwright_page_methods": [
                        PageMethod(
                            "wait_for_function",
                            """() => window.map &&
                            typeof window.map.eachLayer === 'function'""",
                            timeout=50000,
                        ),
                        PageMethod("wait_for_timeout", 2000),
                        PageMethod(
                            "evaluate",
                            """() => {
                                const markers = [];

                                window.map.eachLayer(layer => {
                                    if (!(layer instanceof L.Marker)) return;

                                    const popup = layer.getPopup();
                                    if (!popup) return;

                                    const html = popup.getContent();
                                    const doc = new DOMParser().parseFromString(html, "text/html");

                                    const titleElement = doc.querySelector("a");
                                    const rawHref = titleElement?.getAttribute("href");
                                    const localisation = doc.querySelector('br')?.nextSibling?.textContent.trim();

                                    markers.push({
                                        nom: titleElement?.textContent?.trim() || null,
                                        url: rawHref
                                            ? new URL(rawHref, window.location.href).href
                                            : null,
                                        localisation: localisation,
                                        lat: layer.getLatLng().lat,
                                        lng: layer.getLatLng().lng,
                                    });
                                });

                                return markers;
                            }"""
                        ),
                    ],
                }
            )

    # =============================
    # Extract Leaflet markers
    # =============================
    def parse_map(self, response):
        page_methods = response.meta["playwright_page_methods"]
        markers = page_methods[2].result

        self.logger.info(f"Extracted {len(markers)} markers from map")

        # Initialize Rich progress
        self.progress.start()

        self.progress_task = self.progress.add_task(
            "Scraping Adaptaville",
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

            item = AdaptavilleItem()

            item["nom"] = marker.get("nom")
            item["lat"] = marker.get("lat")
            item["lng"] = marker.get("lng")

            item["type"] = extracted_data.get("type")
            item["description"] = extracted_data.get("description")
            item["url"] = extracted_data.get("url") or marker.get("url")
            item["image_url"] = extracted_data.get("image_url")
            item["aleas"] = extracted_data.get("aleas")
            item["porteurs"] = extracted_data.get("porteurs")
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
        item = AdaptavilleItem()

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