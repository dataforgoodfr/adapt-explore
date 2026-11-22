from sources.csv_adapt import pipeline as csv_adapt
from sources.url import pipeline as url

from sources.ademe import pipeline as ademe
from sources.cerema import pipeline as cerema
from sources.csv import pipeline as csv

PIPELINES = {
    "ADEME": ademe.run,
    "url": url.run,
    "CEREMA": cerema.run,
    "CSV": csv.run,
    "CSV_Adapt": csv_adapt.run,
}