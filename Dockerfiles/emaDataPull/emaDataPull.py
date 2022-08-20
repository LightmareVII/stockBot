import os
import json
import alpaca_trade_api as alpaca

smoothing = 2
### read data from file.json - writing will require 'w' permission and json.dump(myFile)
with open('/stockBotData/tickerEMA.json', 'r') as emaFile:
    emaData = json.load(emaFile)

with open('/stockBotData/tickerList.json', 'r') as tickerListFile:
    tickerList = json.load(tickerListFile)['tickerList']

api = alpaca.REST()
bars = api.get_barset(tickerList, 'day', limit=201)
barSet = bars._raw

emaOutput = {'emaList': emaData['emaList'],
             'tickerEMA': {}}

for ticker in barSet.keys():
    emaOutput['tickerEMA'][ticker] = {}
    for emaCount in emaData['emaList']:
        priceAverage = 0
        for dataPoint in barSet[ticker][-emaCount-1:-1:]:
            priceAverage += dataPoint['c']
        emaOld = priceAverage / emaCount
### Change all of this to use the whole
        priceToday = barSet[ticker][-1]['c']
        emaToday = (priceToday*(smoothing/(1+emaCount))) + (emaOld * (1-(smoothing/(1+emaCount))))
        emaOutput['tickerEMA'][ticker][f'ema{emaCount}'] = round(emaToday, 3)

with open('/stockBotData/tickerEMA.json', 'w+') as newEmaFile:
    json.dump(emaOutput, newEmaFile)

for ticker in tickerList:
    path = f'/stockBotData/tickerData/{ticker}.json'
    if not os.path.exists(path):
        tickerData = {}
    else:
        with open(path, 'r') as tickerDataFile:
            tickerData = json.load(tickerDataFile)

    tickerData['dayTradeStatus'] = 'open'

    with open(path, 'w+') as tickerDataFile:
        json.dump(tickerData, tickerDataFile)
