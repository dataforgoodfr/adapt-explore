Dépendance
--------------
Installer la librairie python crawl4ai

Installation
-------------------------
pip install crawl4ai

puis exécuter crawl4ai-setup puis crawl4ai-doctor

Une fois les fichiers sources téléchargés, les commandes s'éxécutent ainsi:
1) charger le llm que vous vous voulez utiliser (ex "qwen3:8b") via ollama:
ollama pull qwen3:8b

2) Lancer le script python:
python scraper.py --urls urls.txt --model qwen3:8b

Le script suit séquentiellement les urls listées dans le fichier "urls.txt" et génère un fichier json de sortie dans /output grace au LLM chargé et conforme �  la structure établie dans "schema.py".
Actuellement le script ne permet pas de scrappé une page de type annuaire qui recenserait un ensemble de projets et initiatives. On pourrait imaginer un autre script qui génere le fichier urls.txt. Puis utiliser ce script pour générer une fiche par url.
