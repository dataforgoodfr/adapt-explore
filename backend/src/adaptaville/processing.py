import re
# import laya
import trafilatura
from trafilatura import extract
from trafilatura.metadata import extract_metadata
from lxml import html as lxml_html



class HTMLProcessor:

    # agent = laya.Agent(vegaml="4b") # the Qwen3.5-4B (JEV like)

    def __init__(self):
        pass

    def process(self, html):

        # Extract main textual content
        page_text = extract(
            html,
            include_comments=False,
            include_tables=True,
            include_links=False,
            favor_precision=True
        )

        # Extract page metadata
        # metadata = extract_metadata(html)

        tree = lxml_html.fromstring(html)
        
        # Type de projet (mapping translation)
        type_projet =  tree.xpath("//p[contains(normalize-space(.), \"Type(s) d'action(s)\")]/following-sibling::div//a/text()")
        type_projet = [projet.strip() for projet in type_projet if projet.strip()]

        # Description (Traitement de text)
        description_elements = tree.xpath('//*[@id="texte-description"]')
        description =  (" ".join(description_elements[0].text_content().split())
                        if description_elements
                        else None
                        )

        # URL (en dehors de site vitrine)
        articles = tree.xpath('//section[.//h3[contains(., "Contact(s)")]]//ul[@id="contacts"]/li/article')
        urls = [
            url
            for article in articles
            for url in article.xpath('.//a[starts-with(@href, "https://")]/@href')
        ]

        # Image URL
        image_url = tree.xpath("//img[contains(@class, 'w100')]/@src")
        image_url = image_url[0] if image_url else None

        # Porteurs (JEV)
        porteur_elements = tree.xpath(
            '//*[contains(translate(normalize-space(.), '
            '"PORTEUR", "porteur"), "porteur")]'
        )

        porteurs = None

        for element in porteur_elements:
            if element.tag in ("b", "strong"):
                porteurs = element.getparent().text_content().strip()
                porteurs = re.sub(
                        r"^Porteur(?:·se)? de projet\s*:\s*",
                        "",
                        porteurs,
                        flags=re.IGNORECASE
                    ).strip()
                break
                

        # Aleas
        aleas = tree.xpath("//a//div[contains(@class, 'prm')]/text()")
        aleas = [alea.strip() for alea in aleas if alea.strip()]

        # Organisation

        # Localisation
        localisation = tree.xpath("normalize-space(//*[@id='adresse'])")

        # Maturite (JEV)

        # Commentaire 

        # Email (Accessible dans pdf) & Contact
        contact_element = tree.xpath('//*[@id="texte-intro-contacts"]')

        contact_data = {
            "contact": None,
            "email": None,
        }

        if contact_element:
            element = contact_element[0]

            contact_data["contact"] = [
                text.strip()
                for text in element.xpath('.//text()')
                if text.strip()
            ]

            for link in element.xpath('.//a[@href]'):
                href = link.get("href", "").strip()

                if href.lower().startswith("mailto:"):
                    contact_data["email"] = href[7:].split("?")[0].strip()

        return {
            "type": type_projet,
            "description": description,
            "url": urls,
            "image_url": image_url,
            "aleas": aleas,
            "porteurs": porteurs,
            "email": contact_data["email"],
            "contact": contact_data["contact"],
            "localisation": localisation,
            "page_text": page_text or "",
        }
