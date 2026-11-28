#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 20 08:40:49 2026

@author: pierre
"""
import asyncio
import argparse
import json
import os
import random
from urllib.parse import urlparse

from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode, LLMConfig
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from crawl4ai.content_filter_strategy import PruningContentFilterLXML
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
from schema import FicheInitiative


# Fonction pour lire les urls dans le fichier "urls.txt"

def load_urls(file_path: str) -> list[str]:
    with open(file_path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]


# Fonction pour lire le prompt du fichier "prompt.txt"

def load_prompt(file_path: str) -> str:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Le fichier de prompt est introuvable : {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read().strip()
    if not content:
        raise ValueError(f"Le fichier de prompt est vide : {file_path}")
    return content


# Fonction pour transformer l'url scrappée en nom de fichier

def url_to_filename(url: str) -> str:
    parsed = urlparse(url)
    clean_name = f"{parsed.netloc}{parsed.path}".replace("/", "_").strip("_")
    return f"{clean_name[:100]}.json"

# Fonction de scrapping séquentielle des urls listées dans le fichier "urls.txt"

async def process_urls(urls: list[str], model_name: str, prompt_text: str, output_dir: str):
    os.makedirs(output_dir, exist_ok=True)

    # 1. Configuration du LLM local via Ollama passer en argument --model llmName (par défault qwen3:8b)
    # Attention : il faut que ollama soit charger et actif (ollama pull llmName)
    llm_config = LLMConfig(
        provider=f"ollama/{model_name}",
        base_url="http://localhost:11434",
        api_token="no-token"
    )

    # 2. Stratégie d'extraction utilisant le schéma Pydantic de "formatFiche.py" et le prompt de "prompt.txt"
    extraction_strategy = LLMExtractionStrategy(
        llm_config=llm_config,
        schema=FicheInitiative.model_json_schema(),
        extraction_type="schema",
        instruction=prompt_text,
        apply_chunking=False,
        # Utiliser "fit_markdown" si md_generator est actif, sinon "markdown"
        input_format="fit_markdown",
        extra_args={
            "temperature": 0.1,
            "num_ctx": 16384
        }
    )

    # 3. Configuration du filtre de contenu (nettoyage des menus/footers)
    # Pour désactiver le filtrage : commentez les 3 lignes ci-dessous
    # et passez input_format="markdown" dans extraction_strategy plus haut.
    md_generator = DefaultMarkdownGenerator(
        content_filter=PruningContentFilterLXML(threshold=0.45, threshold_type="dynamic")
    )

    # 4. Configuration du navigateur et des règles de crawl
    browser_config = BrowserConfig(
    browser_type="chromium",
    headless=True,  # Plus rapide et fonctionne sans écran (serveur/Docker)
    headers={
        "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
    },
    verbose=False
    )
    run_config = CrawlerRunConfig(
        extraction_strategy=extraction_strategy,
        markdown_generator=md_generator,
        cache_mode=CacheMode.BYPASS,
        word_count_threshold=50,
        check_robots_txt=True, # Respecte les consignes pour les robots des sites visités
#        magic=True,                # Active les contournements anti-bot intégrés de Crawl4AI
#        simulate_user=True,        # Simule des mouvements de souris et un comportement humain
#        override_navigator=True,   # Falsifie les propriétés du navigateur pour masquer l'automatisation
        delay_before_return_html=2.0  # Laisse le temps aux scripts de vérification JS de s'exécuter
    )

    # 6. Exécution du crawl et sauvegarde des fiches
    async with AsyncWebCrawler(config=browser_config) as crawler:
        for i, url in enumerate(urls):
            filepath = os.path.join(output_dir, url_to_filename(url))

            # 6-1. Vérification d'existence des urls, on ignore si ca à déjà été scrappé
            if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
                print(f"[IGNORÉ] Fiche déjà existante : {filepath}")
                continue

            # 6-2. Pause anti-blocage temps aléatoire avant la requête (simule un comportement humain)
            # cela n'est pas toujours nécessaire, ca dépend du site scrappé
            # on pourrait imaginer activer ou pas ce comportement selon le comportement du site visité
            if i > 0:
                pause = random.uniform(3.0, 7.0)
                print(f"Pause anti-blocage de {pause:.1f}s...")
                await asyncio.sleep(pause)

            # 6-3. Crawl et extraction d'une seule URL à la fois à l'aide du LLM local 
            # et dans le format définit dans formatFiche.py
            print(f"Analyse en cours : {url} ...")
            result = await crawler.arun(url=url, config=run_config)

            # 6-4. Nettoyage du résultat et enregistrement
            if result.success and result.extracted_content:
                try:
                    data = json.loads(result.extracted_content)

                    if isinstance(data, list) and len(data) > 0:
                        data = data[0]

                    if isinstance(data, dict):
                        data.pop("error", None)
                        fiche_finale = {"Url": result.url, **data}
                    else:
                        # A revoir: doit me donner le bon format de sortie ou ecrire une erreure
                        fiche_finale = {"Url": result.url, "donnees_brutes": data}

                    # Utilisez le 'filepath' calculé avec 'url' pour garder exactement le même nom de fichier
                    with open(filepath, "w", encoding="utf-8") as f:
                        json.dump(fiche_finale, f, ensure_ascii=False, indent=2)
                    print(f"[OK] Fiche générée : {filepath}")
                except json.JSONDecodeError:
                    print(f"[ERREUR JSON] JSON invalide renvoyé pour {result.url}")
            else:
                print(f"[ÉCHEC] {result.url} -> {result.error_message}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Générateur de fiches JSON via Crawl4AI et Ollama")
    parser.add_argument("--urls", required=True, help="Chemin vers le fichier contenant les URLs")
    parser.add_argument("--model", default="qwen3:8b", help="Nom du modèle Ollama")
    parser.add_argument("--prompt", default="prompt.txt", help="Chemin vers le fichier texte du prompt")
    parser.add_argument("--output", default="output", help="Dossier de sortie des fichiers JSON")
    
    args = parser.parse_args()
    
    url_list = load_urls(args.urls)
    prompt_instruction = load_prompt(args.prompt)
    
    print(f"Traitement de {len(url_list)} URLs | Modèle : '{args.model}' | Prompt : '{args.prompt}'")
    asyncio.run(process_urls(url_list, args.model, prompt_instruction, args.output))