from sources.ademe import pipeline as ademe
from sources.api import pipeline as api
from sources.cerema import pipeline as cerema
from sources.csv import pipeline as csv

PIPELINES = {
    "ADEME": ademe.run,
    "api": api.run,
    "CEREMA": cerema.run,
    "CSV": csv.run,
}