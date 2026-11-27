
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

from collections import defaultdict

from adapt_spider.items.initiative import InitiativeItem
from adapt_spider.processors.adaptaville import AdaptavilleProcessor

class AdaptavilleSpider(scrapy.Spider):
    name = "adaptaville"
    allowed_domains = ["adaptaville.fr"]
    start_urls = ["https://www.adaptaville.fr/carte"]

    def __init__(self, *args, **kwargs):

        # Initialise Driver
        super().__init__(*args, **kwargs)

        self.processor = AdaptavilleProcessor()
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
        markers = page_methods[1].result # markers from map

        self.logger.info(f"Extracted {len(markers)} markers from map")

        # Group markers by URL
        markers_by_url = defaultdict(list)

        for marker in markers:
            url = marker.get("url")
            if url:
                markers_by_url[url].append(marker)

        self.logger.info(
            f"Found {len(markers_by_url)} unique URLs "
            f"for {sum(len(m) for m in markers_by_url.values())} markers"
        )

        # Rich progress: one task per unique page
        self.progress.start()

        self.progress_task = self.progress.add_task(
            "Scraping Adaptaville",
            total=len(markers_by_url),
        )

        # Request each unique URL only once
        for url, associated_markers in markers_by_url.items():
            yield scrapy.Request(
                url=url,
                callback=self.parse_detail,
                errback=self.handle_error,
                cb_kwargs={"markers": associated_markers},
                meta={"playwright": True},
            )

    # =============================
    # Extract information from each page 
    # using `processor`
    # =============================
    def parse_detail(self, response, markers):
        try:
            extracted_data = self.processor.process(response.text)

            for marker in markers:
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
                item["domaine"] = extracted_data.get("domaine")

                item["localisation"] = (
                    marker.get("localisation")
                    or extracted_data.get("localisation")
                )

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

            for marker in markers:
                yield self.build_failed_item(
                    response.url,
                    marker,
                    str(exc),
                )

        finally:
            self.advance_progress()

    def handle_error(self, failure):
        request = failure.request

        self.logger.error(
            f"Request failed: {request.url} - {failure.value}"
        )

        markers = request.cb_kwargs.get("markers")

        if markers:
            for marker in markers:
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