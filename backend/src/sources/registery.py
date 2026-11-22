from sources.ademe import pipeline as ademe
from sources.url import pipeline as url
from sources.cerema import pipeline as cerema
from sources.csv import pipeline as csv
from sources.csv_adapt import pipeline as csv_adapt


PIPELINES = {
    "ADEME": ademe.run,
    "url": url.run,
    "CEREMA": cerema.run,
    "CSV": csv.run,
    "CSV_Adapt": csv_adapt.run,
}