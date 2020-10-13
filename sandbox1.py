import requests
from main import stock_set
stock_set = list(stock_set)
stock_set = stock_set[1:len(stock_set) - 1] # get rid of the first element, which is ""
key = 'ARJTRG5ZQH4Y6MWQJLA0LLHUZVZBU21S'

url = 'https://api.tdameritrade.com/v1/marketdata/quotes'

def getQuotes(**kwargs):
    params = {}
    params.update({'apikey': key})

    symbol_list = []

    for symbol in kwargs.get('symbol'):
        symbol_list.append(symbol)

    params.update({'symbol': symbol_list})

    return requests.get(url, params=params).json()

def getOHLC(**kwargs):
    data = getQuotes(symbol=kwargs.get('symbol'))
    for symbol in kwargs.get('symbol'):
        print(symbol)
        print(data[symbol]['openPrice'],
              data[symbol]['highPrice'],
              data[symbol]['lowPrice'],
              data[symbol]['closePrice'])


#print(getQuotes(symbol=['AAPL', 'TSLA', 'AMD']))
getOHLC(symbol=stock_set)

