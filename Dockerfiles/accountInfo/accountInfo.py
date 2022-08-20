import json
import alpaca_trade_api as alpaca

#setup for paper#

api = alpaca.REST()

paperAccount = api.get_account()._raw
paperPositions = [position._raw for position in api.list_positions()]
paperOpenOrders = [openOrder._raw for openOrder in api.list_orders(status='open', limit=50)]
print(paperAccount)
print(paperPositions)
print(paperOpenOrders)

accountInfo = {"live": {"buyingPower": "",
                        "cash": "",
                        "daytrade_count": "",
                        "daytrading_buying_power": "",
                        "equity": "",
                        "positions": []},
               "paper": {"buyingPower": paperAccount['buying_power'],
                         "cash": paperAccount['cash'],
                         "daytradeCount": paperAccount['daytrade_count'],
                         "daytradingBuyingPower": paperAccount['daytrading_buying_power'],
                         "equity": paperAccount['equity'],
                         "positions": paperPositions,
                         "openOrders": paperOpenOrders}
               }

with open('/stockBotData/accountInfo.json', 'w+') as accountInfoFile:
    json.dump(accountInfo, accountInfoFile)
