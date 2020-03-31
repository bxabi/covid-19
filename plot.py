import plotly.express as px

import pandas as pd


class CoronaPlot:
    def __init__(self):
        self.population = {}
        self.data = []
        self.mapView = []
        self.orderedCountries = []

        self.loadPopulation()
        self.loadCoronaData()

    def loadPopulation(self):
        populationData = pd.read_csv('data/population.csv', '\t')
        for line in populationData.values:
            self.population[line[2].upper()] = line[77].replace(' ', '')
        self.population['SAN MARINO'] = 0
        self.population['ANDORRA'] = 0

    def loadCoronaData(self):
        alldata = pd.read_excel('data/COVID-19-worldwide.xlsx')
        for line in alldata.values:
            self.data.append({'date': line[0], 'newDeaths': line[5], 'country': line[6].upper().replace('_', ' '),
                              'population': line[9]})
        self.data.reverse()

        total = 0
        last = ''
        for index in range(len(self.data)):
            current = self.data[index]
            if current['country'] != last:  # data for a new country starts.
                last = current['country']
                total = 0
                if last in self.population:
                    pop = int(self.population[last])
                else:
                    print("Population of " + last + " is not found.")
                    pop = 0
                    # pop = current['population'] / 1000
                # print(last + " - UN Population:" + str(pop) + ", WB population:" + str(current['population'] / 1000))

            total += current['newDeaths']
            current['total'] = total
            if pop > 0:
                pp = total * 100 / (pop * 1000)
                current['perPopulation'] = pp  # how many %
                current['dailyPerPopulation'] = current['newDeaths'] * 100 / (pop * 1000)  # how many %

                oneIn = 0
                if total > 0:
                    oneIn = pop * 1000 / total
                current['oneIn'] = oneIn

                # store the last value for the map view.
                if index == len(self.data) - 1 or last != self.data[index + 1]['country']:
                    infectionRate = current['newDeaths'] * 100 / (pop * 1000)
                    self.mapView.append({'country': last, 'total': total, 'perPopulation': pp, 'oneIn': oneIn,
                                         'lastDay': current['newDeaths'], 'lastInfectionRate': infectionRate})

            else:
                current['perPopulation'] = 0
                current['oneIn'] = 0

        def getPP(elem):
            return elem['perPopulation']

        self.mapView.sort(key=getPP, reverse=True)
        for i in range(0, len(self.mapView) - 1):
            self.orderedCountries.append(self.mapView[i]['country'])

    def createPlots(self):
        fig = px.line(self.data, x='date', y='newDeaths', color='country', title="Number of deaths / date / country",
                      labels={"date": "Date", "newDeaths": "New Deaths", "country": "Country"},
                      category_orders={'country': self.orderedCountries},
                      color_discrete_sequence=px.colors.qualitative.Alphabet)
        fig.write_html("../Website/generated/daily-deaths.html")

        fig = px.line(self.data, x='date', y='dailyPerPopulation', color='country',
                      title="Deaths / popluation / date / country",
                      labels={"date": "Date", "newDeaths": "New Deaths", "country": "Country",
                              "dailyPerPopulation": "New deaths per population"},
                      category_orders={'country': self.orderedCountries},
                      color_discrete_sequence=px.colors.qualitative.Alphabet,
                      hover_data=["newDeaths"])
        fig.write_html("../Website/generated/daily-deaths-per-population.html")

        fig = px.line(self.data, x='date', y='total', color='country', title="Total deaths per country",
                      labels={"date": "Date", "total": "Total Deaths", "country": "Country"},
                      category_orders={'country': self.orderedCountries},
                      color_discrete_sequence=px.colors.qualitative.Alphabet)
        fig.write_html("../Website/generated/total-deaths.html")

        fig = px.line(self.data, x='date', y='perPopulation', color='country',
                      title="% of population died",
                      labels={"date": "Date", "perPopulation": "Population %",
                              "country": "Country", 'oneIn': 'One In ... people',
                              "total": "Total"},
                      category_orders={'country': self.orderedCountries}, hover_data=['total', 'oneIn'],
                      color_discrete_sequence=px.colors.qualitative.Alphabet)
        fig.write_html("../Website/generated/total-deaths-per-population.html")

    def drawOnMap(self):
        # temps, geyser, gray_r, burg
        fig = px.choropleth(self.mapView, locations="country", locationmode="country names", color="perPopulation",
                            hover_data=["total", "oneIn"], color_continuous_scale='temps',
                            projection='orthographic',
                            labels={"perPopulation": "Population %", "country": "Country",
                                    'oneIn': 'One In ... people',
                                    "total": "Total"}, title="% of population died")
        fig.write_html("../Website/generated/total-deaths-per-population-map.html")

        fig = px.choropleth(self.mapView, locations="country", locationmode="country names", color="lastInfectionRate",
                            hover_data=["lastDay"], color_continuous_scale='temps',
                            projection='orthographic',
                            labels={"lastInfectionRate": "% of population died on the last day", "country": "Country",
                                    "lastDay": "Died on the last day"},
                            title="% of population died on the last day - Presumably correlated to infection rate 2-3 weeks ago")
        fig.write_html("../Website/generated/infection-rate.html")


if __name__ == '__main__':
    plot = CoronaPlot()
    plot.createPlots()
    plot.drawOnMap()
