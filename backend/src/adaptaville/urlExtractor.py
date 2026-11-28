import asyncio
import re
from urllib.parse import urljoin, urlparse
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig

# =====================================================================
# CONFIGURATION
# =====================================================================

URL_CARTE = "https://www.adaptaville.fr/carte"
USER_AGENT = "robotPierre"


def generer_nom_fichier(url: str) -> str:
    """Extrait le nom de domaine et retourne 'urls-nomDomaine.txt'."""
    domaine = urlparse(url).netloc
    # Supprime 'www.' s'il est présent et retire un éventuel numéro de port (:8080)
    domaine = re.sub(r"^www\.", "", domaine).split(":")[0]
    # Remplace les points par des tirets (ex: exemple-carte.fr -> exemple-carte-fr)
    domaine_propre = domaine.replace(".", "-")
    return f"urls-{domaine_propre}.txt"


async def extraire_et_sauvegarder_urls(url_page: str):
    fichier_sortie = generer_nom_fichier(url_page)

    # Expression régulière : capture l'URL dans href="..." après marker.bindPopup("<a
    motif = r'marker\.bindPopup\(\s*["\']<a[^>]+href=\\?["\']([^"\'\\]+)'

    browser_conf = BrowserConfig(
        headless=True,
        user_agent=USER_AGENT,
    )
    run_conf = CrawlerRunConfig(
        check_robots_txt=True,
    )

    async with AsyncWebCrawler(config=browser_conf) as crawler:
        print(f"🔍 Analyse de la page : {url_page}...")
        res = await crawler.arun(url=url_page, config=run_conf)

        if not res.success:
            print(f"❌ Erreur lors du chargement : {res.error_message}")
            return

        # Application de la regex sur le HTML complet rendu par le navigateur
        liens_bruts = re.findall(motif, res.html, re.IGNORECASE)

        # Conversion en URLs absolues, suppression des doublons et tri alphabétique
        urls_propres = sorted({urljoin(url_page, lien) for lien in liens_bruts})

        # Écriture dans le fichier .txt (une URL par ligne)
        with open(fichier_sortie, "w", encoding="utf-8") as f:
            for url in urls_propres:
                f.write(url + "\n")

        print(f"✅ {len(urls_propres)} URL(s) enregistrée(s) dans '{fichier_sortie}'.")


if __name__ == "__main__":
    asyncio.run(extraire_et_sauvegarder_urls(URL_CARTE))