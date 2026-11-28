import re
from urllib.parse import urlparse
import requests

# Ici on tente de capturer les urls d'intéret à partir du siteMap.xml et d'une expression régulière
# L'adresse du siteMap.xml
URL_XML = "https://www.adaptation-changement-climatique.gouv.fr/sitemap.xml"

def generer_nom_fichier(url: str) -> str:
    """Extrait le nom de domaine et retourne 'urls-nomDomaine.txt'."""
    domaine = urlparse(url).netloc
    # Supprime 'www.' s'il est présent et retire un éventuel numéro de port (:8080)
    domaine = re.sub(r"^www\.", "", domaine).split(":")[0]
    # Remplace les points par des tirets (ex: exemple-carte.fr -> exemple-carte-fr)
    domaine_propre = domaine.replace(".", "-")
    return f"urls-{domaine_propre}.txt"


def extraire_urls_sitemap(url_sitemap: str):
    # 1. Téléchargement du sitemap
    resp = requests.get(url_sitemap, headers={"User-Agent": "robotPierre"})
    resp.raise_for_status()

    # 2. Extraction des <loc> et filtrage sur le motif demandé
    toutes_les_urls = re.findall(r"<loc>\s*(.*?)\s*</loc>", resp.text)
    urls_filtrees = sorted({u for u in toutes_les_urls if "/s-inspirer/projetotheque/" in u})

    # 3. Génération du nom de fichier 
    fichier_sortie = generer_nom_fichier(url_sitemap)

    # 4. Écriture du fichier (une URL par ligne)
    with open(fichier_sortie, "w", encoding="utf-8") as f:
        f.write("\n".join(urls_filtrees) + "\n")

    print(f"✅ {len(urls_filtrees)} URLs enregistrées dans '{fichier_sortie}'.")


# Exemple d'utilisation
if __name__ == "__main__":
    extraire_urls_sitemap(URL_XML)