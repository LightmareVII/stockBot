import os
import json
import alpaca_trade_api as alpaca

mySymbol = os.getenv('symbol')
smoothing = 2
desiredStock = 0

api = alpaca.REST()

### Ingest Data from Files
with open(f'/stockBotData/tickerEMA.json', 'r') as tickerDataFile:
    emaData = (json.load(tickerDataFile))['tickerEMA'][mySymbol]
    print(emaData)

with open(f'/stockBotData/tickerData/{mySymbol}.json', 'r') as tickerDataFile:
    tickerData = json.load(tickerDataFile)
    if 'dayTradeStatus' not in tickerData.keys():
        tickerData['dayTradeStatus'] = 'open'
    print(tickerData)

with open(f'/stockBotData/accountInfo.json', 'r') as accountInfoFile:
    accountInfo = json.load(accountInfoFile)['paper']
    allPositions = accountInfo.pop('positions')
    openOrders = accountInfo.pop('openOrders')
    accountInfo['buyingPower'] = float(accountInfo['buyingPower'])
    print(accountInfo)

holdingList = [data['symbol'] for data in allPositions]
openSymbolList = [data['symbol'] for data in openOrders]

print(holdingList)
if mySymbol not in holdingList:
    myPosition = {'qty': 0}
else:
    for position in allPositions:
        if position['symbol'] == mySymbol:
            myPosition = position
            myPosition['qty'] = int(myPosition['qty'])

print('Open Symbols:\n', openSymbolList)
print('My Position:\n', myPosition)

priceToday = float(tickerData['lastClose'])

###
### Calculate New EMA
###

# Remove Unnecessary datapoints
print(f'ema50: {emaData["ema50"]}')
print(f'ema200: {emaData["ema200"]}')
del emaData['ema50']
del emaData['ema200']

# Calculate New EMAs with current price
for ema in emaData.keys():
    emaCount = int(ema.strip('ema'))
    emaOld = emaData[ema]
    emaData[ema] = (priceToday * (smoothing / (1 + emaCount))) + (emaOld * (1 - (smoothing / (1 + emaCount))))

###
### Prep & Trade
###

# Calculate how many stock is desired
for emaKey in list(emaData.keys())[1:]:
    if priceToday > emaData[emaKey]:
        desiredStock += 2

# Contains datapoints for market open/close
marketClockInfo = api.get_clock()

print(mySymbol)
print(f'Desired: {desiredStock}')
print(f'Owned: {myPosition["qty"]}')

# Trade - Not if any open orders or market is closed
if mySymbol not in openSymbolList:
    if marketClockInfo.is_open:
        print('Market Open')
        if desiredStock < int(myPosition['qty']):
            if tickerData['dayTradeStatus'] == 'open' or tickerData['dayTradeStatus'] == 'sell':
                quantity = myPosition['qty'] - desiredStock

                api.submit_order(symbol=mySymbol,
                                 qty=quantity,
                                 side='sell',
                                 type='market',
                                 time_in_force='day')
                print(f'Selling {mySymbol}: {quantity}')
            else:
                print('Sell Attempt: Day Trade Protection')
                tickerData['dayTradeStatus'] = 'sell'
        elif desiredStock > myPosition['qty']:
            if accountInfo['buyingPower'] > (priceToday * desiredStock):
                if tickerData['dayTradeStatus'] == 'open' or tickerData['dayTradeStatus'] == 'buy':
                    quantity = desiredStock - myPosition['qty']

                    api.submit_order(symbol=mySymbol,
                                     qty=quantity,
                                     side='buy',
                                     type='market',
                                     time_in_force='day')
                    print(f'Buying {mySymbol}: {quantity}')
                    tickerData['dayTradeStatus'] = 'buy'
                else:
                    print('Buy Attempt: Day Trade Protection')
            else:
                print(f'I want to buy {mySymbol}: Not Enough Buying Power')
    else:
        print('Market Closed')
else:
    print(f'Terminating {mySymbol} evaluation: Position Already Open')

with open(f'/stockBotData/tickerData/{mySymbol}.json', 'w') as tickerDataFile:
    json.dump(tickerData, tickerDataFile)
    print(tickerData)
