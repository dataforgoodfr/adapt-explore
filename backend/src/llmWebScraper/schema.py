#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 20 08:37:09 2026

@author: pierre
"""

from typing import Literal, Optional
from pydantic import BaseModel, Field

# Définition des nomenclatures fermées (génère des contraintes enum strictes)
TypeInitiativeEnum = Literal[
    "Outil ou service",
    "Initiative de terrain",
    "Source d'information",
    "Guide ou méthode",
    "Entreprise",
]

AleaEnum = Literal[
    "Transversal",
    "Canicule et chaleur",
    "Sécheresse",
    "Inondation pluviale",
    "Inondation fluviale",
    "Submersion marine et érosion côtière",
    "Retrait-gonflement des argiles",
    "Incendie et dépérissement forestier",
    "Tempête et vent violent",
    "Mouvement de terrain",
    "Grêle",
    "Autre",
]

TypePorteurEnum = Literal[
    "Collectivité",
    "Entreprise",
    "État et opérateur public",
    "Association",
    "Recherche",
    "Mixte",
    "Autre",
]

MaturiteEnum = Literal[
    "Déployé et évalué avec résultats",
    "Déployé",
    "Expérimentation",
    "Idée",
]

DomainEnum = Literal[
    "Bâtiment",
    "Espace public et urbanisme",
    "Eau",
    "Agriculture et alimentation",
    "Forêt et biodiversité",
    "Santé et social",
    "Mobilité et infrastructures",
    "Économie et emploi",
    "Culture et patrimoine",
    "Gouvernance et organisation",
]


class FicheInitiative(BaseModel):
    Url: Optional[str] = Field(
        default=None,
        description="URL source de la page web de l'initiative.",
    )
    Type_Initiative: Optional[TypeInitiativeEnum] = Field(
        default=None,
        description="Catégorie de l'initiative selon la nomenclature autorisée, ou null si absent.",
    )
    Lien_image: Optional[str] = Field(
        default=None,
        description="URL complète d'une image pertinente illustrant l'initiative, ou null si absente.",
    )
    Description: Optional[str] = Field(
        default=None,
        description="Description synthétique et fidèle de l'initiative basée uniquement sur l'article.",
    )
    Aleas: list[AleaEnum] = Field(
        default_factory=list,
        description=(
            "Liste des aléas climatiques auxquels l'initiative cherche réellement à répondre. "
            "Retourne une liste vide [] si aucun aléa n'est identifiable."
        ),
    )
    Type_Porteur_Initiative: Optional[TypePorteurEnum] = Field(
        default=None,
        description="Catégorie de l'organisme porteur selon la nomenclature, ou null si absent.",
    )
    Nom_porteur: Optional[str] = Field(
        default=None,
        description="Nom exact de l'organisme qui porte l'initiative, ou null si absent.",
    )
    Localisation: list[str] = Field(
        default_factory=list,
        description="Liste des territoires géographiques concernés (communes, départements, régions, pays). Liste vide [] si absent.",
    )
    Maturite: Optional[MaturiteEnum] = Field(
        default=None,
        description="Niveau de maturité de l'initiative selon la nomenclature, ou null si non précisé.",
    )
    Commentaires: Optional[str] = Field(
        default=None,
        description="Informations complémentaires utiles (partenaires, financements, dates clés), ou null si rien à ajouter.",
    )
    email: Optional[str] = Field(
        default=None,
        description="Adresse e-mail de contact trouvée dans la page, ou null si absente.",
    )
    Domain: Optional[DomainEnum] = Field(
        default=None,
        description="Domaine thématique principal de l'initiative, ou null si absent.",
    )