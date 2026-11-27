import re

import laya
import trafilatura
from trafilatura import extract
from trafilatura.metadata import extract_metadata

from adapt_spider.processors.base import BaseProcessor

#AGENT = laya.Agent(model="multilingual")

# LAYA settings
QUESTIONS = {
    "type_initiative": {
            "type": "choice",
            "instructions": "Quel type d'organisation est résponsable du projet ?",
            "criteria": {
                "collectivité": "municipalité, ville, département, région ou collectivité locale",
                "entreprise": "Société privée ou entreprise commerciale",
                "etat_et_operateur_public": "Gouvernement national, ministère ou opérateur public",
                "association": "Association à but non lucratif, ONG ou fondation",
                "recherche": "Université, institut de recherche ou laboratoire",
                "mixte": "Partenariat impliquant différents types d'organisations",
                "autre": "Organisation autre ou non identifiée"
            }
        },
    "type_porteur_initiative": {
        "type": "choice",
        "instructions": "Quel type d'organisation est résponsable du projet ?",
        "criteria": {
            "collectivité": "municipalité, ville, département, région ou collectivité locale",
            "entreprise": "Société privée ou entreprise commerciale",
            "etat_et_operateur_public": "Gouvernement national, ministère ou opérateur public",
            "association": "Association à but non lucratif, ONG ou fondation",
            "recherche": "Université, institut de recherche ou laboratoire",
            "mixte": "Partenariat impliquant différents types d'organisations",
            "autre": "Organisation autre ou non identifiée"
        }
    },
    "maturite": {
            "type": "choice",
            "instructions": "Quel type d'organisation est le propriétaire du projet ?",
            "criteria": {
                "collectivité": "municipalité, ville, département, région ou collectivité locale",
                "entreprise": "Société privée ou entreprise commerciale",
                "etat_et_operateur_public": "Gouvernement national, ministère ou opérateur public",
                "association": "Association à but non lucratif, ONG ou fondation",
                "recherche": "Université, institut de recherche ou laboratoire",
                "mixte": "Partenariat impliquant différents types d'organisations",
                "autre": "Organisation autre ou non identifiée"
            }
        },
    "domaine": {
        "type": "choice",
        "instructions": "Quel type d'organisation est le propriétaire du projet ?",
        "criteria": {
            "collectivité": "municipalité, ville, département, région ou collectivité locale",
            "entreprise": "Société privée ou entreprise commerciale",
            "etat_et_operateur_public": "Gouvernement national, ministère ou opérateur public",
            "association": "Association à but non lucratif, ONG ou fondation",
            "recherche": "Université, institut de recherche ou laboratoire",
            "mixte": "Partenariat impliquant différents types d'organisations",
            "autre": "Organisation autre ou non identifiée"
        }
    },
}
""" DOMAINE
- Bâtiment
- Espace public et urbanisme
- Eau
- Agriculture et alimentation
- Forêt et biodiversité
- Santé et social
- Mobilité et infrastructures
- Économie et emploi
- Culture et patrimoine
- Gouvernance et organisation
"""

class AdaptavilleProcessor(BaseProcessor):

    def __init__(self):
        pass

    def extract(self, tree):

        # result = AGENT.predict(page_text, QUESTIONS)
        # porteurs_laya = result["answers"]["porteur"]
        # porteurs_laya_choice = porteurs_laya["choice"]
        # porteurs_laya_proba = porteurs_laya["probabilities"]

        # Extract page metadata
        # metadata = extract_metadata(html)
        
        # Type de projet (mapping translation)
        type_initiative =  tree.xpath("//p[contains(normalize-space(.), \"Type(s) d'action(s)\")]/following-sibling::div//a/text()")
        type_initiative = [initiative.strip() for initiative in type_initiative if initiative.strip()]

        # Description (Traitement de text)
        description_elements = tree.xpath('//*[@id="texte-description"]')
        description =  (
                    " ".join(description_elements[0].text_content().split())
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

        # Domaine d'application
        element = tree.xpath('//*[@id="texte-description"]')[0]
        domaine = element.xpath(
            './/b[preceding-sibling::text()[contains(., "Domaine")]]/text()'
        )

        domaine = list(dict.fromkeys(
            value.strip()
            for value in domaine
            if value.strip()
        ))

        return {
            "type_initiative": type_initiative,
            "description": description,
            "url": urls,
            "image_url": image_url,
            "aleas": aleas,
            "porteurs": porteurs,
            "domaine":domaine,
            "localisation": localisation,
            #"porteurs_laya_choice": porteurs_laya_choice,
            #"porteurs_laya_proba": porteurs_laya_proba,
            "email": contact_data["email"],
            "contact": contact_data["contact"],
        }