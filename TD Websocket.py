import PlayTypeNegativeOnePointOne
from main import stock_set
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
import threading
import time
stock_list = list(stock_set)
for stock in stock_list:
    print("THIS THE REDSPROUT HIGH AND LOW for ", stock, " ",PlayTypeNegativeOnePointOne.bigloopType4(stock))


