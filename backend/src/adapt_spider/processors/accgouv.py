import re

import logging
import laya
import trafilatura
from trafilatura import extract
from trafilatura.metadata import extract_metadata

from adapt_spider.processors.base import BaseProcessor


logger = logging.getLogger(__name__)

#AGENT = laya.Agent(model="multilingual")

class ACCGouvProcessor(BaseProcessor):

    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)

    def extract(self, tree):

        # result = AGENT.predict(page_text, QUESTIONS)
        # porteurs_laya = result["answers"]["porteur"]
        # porteurs_laya_choice = porteurs_laya["choice"]
        # porteurs_laya_proba = porteurs_laya["probabilities"]

        # Extract page metadata
        # metadata = extract_metadata(html)

        # Tableau Caractéristiques
        caracteristiques = {}

        fields = tree.xpath(
            "//div[contains(concat(' ', normalize-space(@class), ' '), ' pane-term ')]"
            "//div[contains(concat(' ', normalize-space(@class), ' '), ' field ')]"
        )

        for field in fields:
            label = field.xpath(
                "normalize-space(./div[contains(concat(' ', normalize-space(@class), ' '), ' field__label ')])"
            )

            values = field.xpath(
                ".//div[contains(concat(' ', normalize-space(@class), ' '), ' field__item ')]"
                "//text()[normalize-space()]"
            )

            values = [value.strip() for value in values if value.strip()]

            if label and values:
                caracteristiques[label] = values

        logger.info(caracteristiques)
        
        # Type de projet (mapping translation)
        type_initiative = caracteristiques.get("Type d'action") or caracteristiques.get("Public cible")

        # Description (Traitement de text)
        desc = {}

        fields = tree.xpath(
            "//div[contains(concat(' ', normalize-space(@class), ' '), ' text-formatted ')]"
            "[contains(concat(' ', normalize-space(@class), ' '), ' field ')]"
        )

        for field in fields:
            label = field.xpath(
                "normalize-space(./div[contains(concat(' ', normalize-space(@class), ' '), ' field__label ')])"
            )

            content = field.xpath(
                "./div[contains(concat(' ', normalize-space(@class), ' '), ' field__item ')]"
            )

            if not label or not content:
                continue

            text = " ".join(content[0].itertext())
            text = " ".join(text.split())

            desc[label] = text

        description = ["".join(d) for d in desc.values()]
        

        # URL
        urls = tree.xpath("//div[contains(concat(' ', normalize-space(@class), ' '), ' field--name-field-link-1 ')]//a/@href")
        
        # Image URL
        
        # Porteurs (JEV)
        porteurs = tree.xpath("normalize-space(//div[contains(@class, 'field--name-field-link-2')]//a)")

        # Aleas
        aleas = caracteristiques["Impact"]

        # Organisation

        # Localisation
        localisation = caracteristiques["Territoire"]

        # Maturite (JEV)

        # Commentaire 
        commentaire = caracteristiques.get("Mots clés", None)

        # Email & Contact (Revoir)
        contact = tree.xpath(
            "string(//div[contains(@class, 'field--name-field-text-2')]//div)"
        )

        contact = contact.replace("\xa0", " ").strip()

        # Domaine d'application
        domaine = caracteristiques["Thématique"]

        return {
            "type_initiative": type_initiative,
            "description": description,
            "url": urls,
            "image_url": None,
            "aleas": aleas,
            "porteurs": porteurs,
            "domaine":domaine,
            "localisation": localisation,
            "email": contact,
            "contact": contact,
            "commentaire": commentaire
        }