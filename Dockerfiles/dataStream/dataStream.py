import os
import requests
import json
from alpaca_trade_api import Stream

gitlabURL = '' # deprecated when moving up to aws
myToken = '' # can be pulled down from alpaca website

with open('/stockBotData/tickerList.json', 'r') as tickerListFile:
    tickerDict = json.load(tickerListFile)
tickerList = tickerDict['tickerList']

### Start Script
async def trade_callback(t):
    print('trade', t)

async def quote_callback(q):
    print('quote', q)

async def bars_callback(myBar):
    barDict = myBar._raw
    print(barDict)
    path = f'/stockBotData/tickerData/{barDict["symbol"]}.json'
    if not os.path.exists(path):
        saveData = {}
    else:
        with open(path, 'r') as tickerDataFile:
            saveData = json.load(tickerDataFile)

    saveData['lastClose'] = barDict['close']
    saveData['vwap'] = barDict['vwap']
    saveData['volume'] = barDict['volume']
    saveData['timestamp'] = barDict['timestamp']

    with open(f'/stockBotData/tickerData/{barDict["symbol"]}.json', 'w+') as tickerDataFile:
        json.dump(saveData, tickerDataFile)

    myData = {'token': myToken,
              'ref': 'main',
              'variables[symbol]': barDict['symbol'],
              'variables[evaluateTrade]': 'true'}

    response = requests.post(gitlabURL, myData)
    print(response.text)
    print("============================================================")

stream = Stream(data_feed="iex")
stream.subscribe_bars(bars_callback, *tickerList)
stream.run()
#