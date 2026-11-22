# Backend ETL

Ce dossier contient le pipeline qui récupère des données de sources externes (open data, API, fichiers, scraping), les stocke à l'état brut, puis transfome et les stockes au bon format dans Postgres.

## Le parcours d'une donnée

- Le driver va chercher le brut et le renvoie par paquets (RawBatch).
- Le stockage écrit ces paquets tels quels dans le raw data (dossier local, puis S3).
- L'extractor relit le brut et le transforme en {colonne: valeur}.
- La validation vérifie les valeurs et met de côté celles qui sont refusées, avec la raison.
- La consolidation gère les doublons
- Le load écrit dans Postgres par upsert.

(Certaines sources n'ont pas de driver, comme les csv ou ils seront directement envoyé sur le S3)

## Ce que fait chaque fichier

### common/ : ce qui est partagé
setting.py : Lit la configuration : chemin du raw data, accès S3, base de données.
base.py : Décrit le modèle que suit tout driver : validate_config, fetch, healthcheck.
raw_store.py : Écrit et relit le brut sous {source}/{run_id}/. 
schema.py : Lit dans Postgres les colonnes de la table cible (nom, type, obligatoire, prompt).
consolidate.py : Gère les doublons. 
load.py : Écrit dans Postgres.

### sources/ : ce qui est propre à chaque source

registry.py : Tableau « nom de la source → son pipeline » ("ademe", "url"...).

Pour chaque source : 
ademe/pipeline.py : Le workflow complet de l'ADEME : dans quel ordre appeler driver, stockage, extractor, validation, load. Chaque source peut avoir un enchaînement différent.
ademe/discovery.py : Facultatif. Trouve des URL supplémentaires à partir de mots-clés et renvoie la liste des URL à récupérer.
ademe/driver.py : Va chercher le brut chez l'ADEME et le renvoie par paquets.
ademe/extractor.py : Transforme le brut en {colonne: valeur} : mappage de colonnes, regex, classifier ou LLM. On privilégie le moins coûteux et le plus prévisible (mappage, regex), le LLM étant réservé à ce qui ne se règle pas autrement.
ademe/validation.py :  Règles : type correct, champs obligatoires présents. Renvoie les valeurs valides et les rejets.
ademe/config.py : Réglages propres à la source : URL, séparateur, correspondance des colonnes.

## Organisation du raw data

raw/
└── {source_id}/
    └── {run_id}/
        ├── part-0001.jsonl      # ou original.csv, page-0001.html...
        └── manifest.json        # date, source, format, fichiers écrits