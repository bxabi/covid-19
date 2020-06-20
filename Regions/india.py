import json
import pandas as pd

from . import tools


class India:
    mapView = []
    population = {}
    plotData = []

    totalDeaths = {}
    lastDayDeaths = {}
    totalCases = {}
    lastDayCases = {}

    def __init__(self):
        with open('data/admin1.geojson') as json_file:
            self.geo = json.load(json_file)

        casesCsv = pd.read_csv('data/India/COVID19_INDIA_STATEWISE_TIME_SERIES_CONFIRMED.csv', ',')
        deathsCsv = pd.read_csv('data/India/COVID19_INDIA_STATEWISE_TIME_SERIES_DEATH.csv', ',')

        for i in range(0, 37):
            row1 = casesCsv.values[i]
            row2 = deathsCsv.values[i]
            state = row1[0]
            pop = int(row1[5].replace(',', ''))
            self.population[state] = pop
            for j in range(8, len(row1)):
                date = casesCsv.columns[6][0]
                self.lastDayCases[state] = row1[j] - row1[j-1]
                self.totalCases[state] = row1[j]
                casesPerPopulation = self.totalCases[state] * 100 / pop
                dailyCasesPerPopulation = self.lastDayCases[state] * 100 / pop  # how many %

                self.lastDayDeaths[state] = row2[j] - row2[j-1]
                self.totalDeaths[state] = row2[j]
                deathsPerPopulation = self.totalDeaths[state] * 100 / pop
                dailyDeathsPerPopulation = self.lastDayDeaths[state] * 100 / pop  # how many %

                self.plotData.append(
                    {"country": state, "date": date,
                     "newCases": self.lastDayCases[state],
                     "newDeaths": self.lastDayDeaths[state], "totalCases": self.totalCases[state],
                     "totalDeaths": self.totalDeaths[state], "deathsPerPopulation": deathsPerPopulation,
                     "casesPerPopulation": casesPerPopulation,
                     "dailyDeathsPerPopulation": dailyDeathsPerPopulation,
                     "dailyCasesPerPopulation": dailyCasesPerPopulation})

        self.geo["features"][:] = [value for value in self.geo["features"] if self.isInIndia(value)]

    def isInIndia(self, object):
        country = object["properties"]["country"]
        if country != "India":
            return False

        state = object["properties"]["name"]
        if state in self.population:
            object["id"] = state
            row = tools.getMapviewRow(state, self.lastDayCases[state], self.lastDayDeaths[state],
                                      self.totalCases[state], self.totalDeaths[state],
                                      self.population[state])
            self.mapView.append(row)
            return True
        # else:
        #     if state is not None:
        #         print(state + " is in India but population is unknown.")

        return False
