# ADAPT SPIDER

Regroupe l'ensemble des crawlers développés pour collecter des données sur différentes plateformes recensant des initiatives d'adaptation.

Les sites actuellement pris en charge sont :

- **Adaptaville** : https://www.adaptaville.fr/
- **Adaptation au changement climatique (Gouvernement)** : https://www.adaptation-changement-climatique.gouv.fr/s-inspirer/projetotheque
- **À venir**: développement de crawlers supplémentaires pour les sites identifiés.

## Collecte des données

### Extraction des initiatives depuis les cartographies

Identifier et extraire les marqueurs (*markers*) présents sur les cartographies des sites.

Exemple : [Cartographie des projets locaux – Adaptation au changement climatique](https://www.adaptation-changement-climatique.gouv.fr/projets-locaux-financements/localisation#paragraph--21879).

Pour chaque marqueur, les informations suivantes sont récupérées :

- **Nom de l'initiative**
- **Latitude**
- **Longitude**
- **URL** : lien vers la page de présentation de l'initiative.

### Extraction des informations clefs au projet

Chaque URL est scrapé afin de récupérer les informations relatives à l'initiative.

Une partie du code permet d'éviter de visiter plusieurs fois une même page.

Les champs extraits sont les suivants :

| Champ |
|---|
| Type d'initiative | 
| Description |
| URL | 
| Image URL | 
| Aléas | 
| Porteurs | 
| Domaine | 
| Localisation |
| Email | 
| Autre contact |
| Page Text |

❌Organisation
❌Maturité
❌Commentaires

## Post-traitement des données (Work in progress)

Un travail  de normalisation (*post-processing*) reste donc nécessaire pour les rendre compatibles avec le format cible.

Plusieurs approches peuvent être éxplorées :

- **Expressions régulières (Regex)**
- **Traitement textuel** : pour nettoyer, structurer et harmoniser les données textuelles.
- **Outils de classification** : [Laya](https://github.com/NandhaKishorM/laya) pour structurer l'information à partir du contenu des pages.

## Format cible des données (*Data Format Requirements*)

### Type d'initiative

- Outil ou service
- Initiative de terrain
- Source d'information
- Guide ou méthode
- Entreprise

### Image et description

- **Lien image** : URL de l'image associée à l'initiative.
- **Description** : présentation synthétique de l'initiative.

### Aléas climatiques

- Transversal
- Canicule et chaleur
- Sécheresse
- Inondation pluviale
- Inondation fluviale
- Submersion marine et érosion côtière
- Retrait-gonflement des argiles
- Incendie et dépérissement forestier
- Tempête et vent violent
- Mouvement de terrain
- Grêle
- Autre

### Porteurs de l'initiative

- `Type_Porteur_Initiative`
- `Nom_porteur`

### Localisation

- Localisation géographique ou territoriale de l'initiative.

### Maturité

Les initiatives doivent être classées selon leur niveau de maturité :

- Déployé et évalué avec résultats
- Déployé
- Expérimentation
- Idée

### Autres informations

- Commentaires
- Email
- Domaine

### Domaines d'intervention

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

## Architecture du code
Les crawlers peuvent être lancés a l'aide de la commande suivante :

```bash
python .\backend\run_scraper.py spider_name
```

Le paramètre `spider_name` correspond au crawler :

- `adaptaville`
- `accgouv`

```text
backend/
│
├── data/
│   ├── accgouv.json
│   └── adaptaville.json
│
├── src/
│   ├── adapt_spider/
│   │   ├── DOCS.MD
│   │   ├── settings.py
│   │   │
│   │   ├── items/
│   │   │   └── initiative.py
│   │   │
│   │   ├── processors/
│   │   │   ├── accgouv.py
│   │   │   ├── adaptaville.py
│   │   │   └── base.py
│   │   │
│   │   └── spiders/
│   │       ├── accgouv.py
│   │       └── adaptaville.py
│   │
│   ├── run_scraper.py
│   └── scrapy.cfg
```

| Composant | Rôle |
|---|---|
| `data/` | Stockage des données collectées au format JSON, avec un fichier par source. |
| `settings.py` | Configuration générale des crawlers : paramètres de téléchargement, gestion des requêtes, intégration de Playwright, etc. |
| `items/initiative.py` | Définition des champs associés à une initiative. |
| `processors/` | Traitement du HTML et extraction des informations correspondant aux différents champs requis. Chaque source dispose de son propre processor. |
| `spiders/` | Définition des crawlers propres à chaque plateforme. Requêtes JavaScript nécessaires à l'extraction des marqueurs des cartographie et transmettent les pages récupérées au processor correspondant. |
| `run_scraper.py` | Script permettant de simplifier le lancement des différents crawlers. |
| `scrapy.cfg` | Fichier de configuration du projet Scrapy |
