from ib.opt import Connection, message
from ib.ext.Contract import Contract
from ib.ext.Order import Order
from ib.opt import ibConnection
import PlayTypeNegativeOnePointOne
from main import stock_set





def make_contract(symbol, sec_type, exch, prim_exch, curr):
    Contract.m_symbol = symbol
    Contract.m_secType = sec_type
    Contract.m_exchange = exch
    Contract.m_primaryExch = prim_exch
    Contract.m_currency = curr
    return Contract


def make_order(action, quantity, price=None):
    if price is not None:
        order = Order()
        order.m_orderType = 'LMT'
        order.m_totalQuantity = quantity
        order.m_action = action
        order.m_lmtPrice = price

    else:
        order = Order()
        order.m_orderType = 'MKT'
        order.m_totalQuantity = quantity
        order.m_action = action

    return order


cid = 520
stock_list = list(stock_set)#[0:6]
#stock_list = ['NIO', "SPY", "PEIX", "AAPL", "ALT", "CBAT"]
#stock_list = ["CREG"]
boughtList = []
i = 0
while __name__ == "__main__":
    stock = stock_list[i]
    i = i + 1
    if i == len(stock_list):
        i = 0
    redSproutHighAndLowList = PlayTypeNegativeOnePointOne.bigloopType4(stock)
    try:
        redSproutHigh, redSproutLow = redSproutHighAndLowList[0], redSproutHighAndLowList[1]
    except:
        print("Nope")
        continue
    conn = Connection.create(port=7497, clientId=5721)
    conn.connect()
    oid = cid

    cont = make_contract(stock, 'STK', 'SMART', 'SMART', 'USD')
    offer = make_order('BUY', 1, redSproutLow)
    boughtList.append(stock)
    conn.placeOrder(oid, cont, offer)
    #tws = ibConnection(host='localhost', port=7497, clientId=5721)
    #tws.reqAccountUpdates(True, 'DU1394632')
    conn.disconnect()
    #x = input('enter to resend')
    cid += 1



