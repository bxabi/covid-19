import json
import pandas as pd

from Generator import tools

stateNames = {"BW": "Baden-Württemberg", "BY": "Bayern", "BE": "Berlin", "BB": "Brandenburg", "HB": "Bremen",
              "HH": "Hamburg", "HE": "Hessen", "NI": "Niedersachsen", "MV": "Mecklenburg-Vorpommern",
              "NW": "Nordrhein-Westfalen", "RP": "Rheinland-Pfalz", "SL": "Saarland", "SN": "Sachsen",
              "ST": "Sachsen-Anhalt", "SH": "Schleswig-Holstein", "TH": "Thüringen"}

population = {"BW": 11069533, "BY": 13076721, "BE": 3644826, "BB": 2511917, "HB": 682986, "HH": 1841179,
              "HE": 6265809, "NI": 7982448, "MV": 1609675,
              "NW": 17932651, "RP": 4084844, "SL": 990509, "SN": 4077937,
              "ST": 2208321, "SH": 2896712, "TH": 2143145}

with open('data/admin1.geojson') as json_file:
    admin1Geo = json.load(json_file)

csv = pd.read_csv('data/Germany/germany.csv', ',')

totalDeaths = {}
lastDayDeaths = {}
totalCases = {}
lastDayCases = {}
for column in csv.items():
    short = column[0][3:5]
    if short in stateNames.keys():
        state = stateNames[short]
        total = column[1].values[-1]
        last = total - column[1].values[-2]
        t = column[0][6:]
        if t == "cases":
            totalCases[state] = total
            lastDayCases[state] = last
        else:
            totalDeaths[state] = total
            lastDayDeaths[state] = last

mapView = []


def getPopulation(state):
    for key, value in stateNames.items():
        if value == state:
            return population[key]


def isInGermany(object):
    country = object["properties"]["country"]
    if country != "Germany":
        return False

    state = object["properties"]["name"]
    if state in stateNames.values():
        object["id"] = state
        row = tools.getMapviewRow(state, lastDayDeaths[state], lastDayDeaths[state], totalCases[state],
                                  totalDeaths[state], getPopulation(state))
        mapView.append(row)
        return True
    return False


admin1Geo["features"][:] = [value for value in admin1Geo["features"] if isInGermany(value)]


def loadCoronaData():
    return mapView, admin1Geo
