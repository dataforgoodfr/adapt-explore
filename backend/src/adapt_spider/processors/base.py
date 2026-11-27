from abc import ABC, abstractmethod

from lxml import html
from trafilatura import extract


class BaseProcessor(ABC):

    def process(self, html_content):

        tree = html.fromstring(html_content)
        page_text = extract(
            html_content,
            include_comments=False,
            include_tables=True,
            include_links=False,
            favor_precision=True,
        )
        data = self.extract(tree)
        data["page_text"] = page_text
        return self.normalize(data)

    @abstractmethod
    def extract(self, tree):
        pass

    def normalize(self, data):
        return data