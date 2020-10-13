import requests
import time
import datetime
from datetime import datetime
from TimSort import merge_sort # merge_sort needs an array
from main import stock_set
import pandas as pd
import warnings
warnings.filterwarnings("ignore")
key = 'ARJTRG5ZQH4Y6MWQJLA0LLHUZVZBU21S'
stock_list = list(stock_set)
stock_list[0]="SRNE"

for stock in stock_list:
    start_date_string = "10/06/2020 04:00:00"
    end_date_string = "10/06/2020 09:29:00"
    # Considering date is in dd/mm/yyyy format
    start_date  = datetime.timestamp(datetime.strptime(start_date_string, "%m/%d/%Y %H:%M:%S"))*1000
    end_date = datetime.timestamp(datetime.strptime(end_date_string, "%m/%d/%Y %H:%M:%S"))*1000
    # 512 is first index val

    isTakeProfitReached = False # false by default
    isType1PointOhPlay = False
    isWin = False
    isStopLossNotReached = False
    # premarket start Friday Oct 9th = 1602230400000
    # premarket end Friday Oct 9th = 1602250140000

    # market open Friday Oct 9th = 1602250200000
    # market close Saturday Oct 10th = 1602273600000




    #stock = "ADMP"

    def getPriceHistory(**kwargs):

        url = 'https://api.tdameritrade.com/v1/marketdata/{}/pricehistory'.format(kwargs.get('symbol'))
        params = {}
        params.update({'apikey': key})

        for arg in kwargs:
            parameter = {arg: kwargs.get(arg)}
            params.update(parameter)


        return requests.get(url, params = params).json()

    def timeOf(dataframe): #we assume that we're passed the dataframe. you pass this a whole fat dataframe
        try:
            return  time.ctime(dataframe['datetime'].min()/1000)
        except:
            print("this is the faulty stock: ", stock)

    friendly_dict = getPriceHistory(symbol=stock, periodType='day', frequencyType='minute', startDate = 1602172800000, endDate = 1602450000000, needExtendedHoursData = True)
    df = pd.DataFrame(friendly_dict['candles'])
    premarketFri_start = df[df['datetime'] >= 1602230400000]
    premarketFri = premarketFri_start[premarketFri_start['datetime'] <= 1602250140000]

    marketFri_start = df[df['datetime'] >= 1602250200000]
    marketFri = marketFri_start[marketFri_start['datetime'] <= 1602273600000]


    #print(time.ctime(premarketFri['datetime'].min()/1000)
     #     , time.ctime(marketFri['datetime'].min()/1000))

    #print("premarket high is: ", premarketFri['high'].max())
    #print("during market hours, high is: ", marketFri['high'].max())

    premarket_high = premarketFri['high'].max()

    #print("this is the time at which pm high is breached: ", timeOf(marketFri[marketFri['high'].gt(premarket_high)])) # shows you which is the first time the premarket high is breached during the market
    # lol it's breached at 512, sure, but marketFri index starts at 504 or smth because it itself is a slice of the original df

    try:
        indexFirstResBreaker = marketFri[marketFri['high'].gt(premarket_high)].index[0]
    except:
        print("this is the faulty stock, cos it doesn't break the PM high: ", stock)
        continue
    #print("this is the index of pm high breach: ", indexFirstResBreaker )

    index_of_breach = marketFri[marketFri['high'].gt(premarket_high)].index[0]
    index_of_marketFriStart = marketFri.index[0]
    relative_index_of_breach = index_of_breach - index_of_marketFriStart


    market_after_breaching_pmhigh = marketFri[relative_index_of_breach+1:] #ignores the first breaking candle

    try:
        index_of_gobackdownbelowpmhighafterbreach = market_after_breaching_pmhigh[market_after_breaching_pmhigh ['low'].lt(premarket_high)].index[0]
    except:
        print("this is the faulty stock because it doesn't go back down again after breaking the res: ", stock)
        continue

    index_of_market_after_breaching_pmhighStart = market_after_breaching_pmhigh.index[0]
    relative_gobackdownbelowpmhighafterbreach = index_of_gobackdownbelowpmhighafterbreach - index_of_market_after_breaching_pmhighStart
    #print(relative_gobackdownbelowpmhighafterbreach)

    #print("this is the point after which market, after breaching Pm high, dipped below again: ", market_after_breaching_pmhigh[relative_gobackdownbelowpmhighafterbreach: ])
    #print("this is the start time of the above phenomenon: ", market_after_breaching_pmhigh[relative_gobackdownbelowpmhighafterbreach: ])

    #print("this is the time that the pm high was dipped below, after having risen above it: ", timeOf(market_after_breaching_pmhigh[relative_gobackdownbelowpmhighafterbreach: ]))

    indexFirstDipDowner = market_after_breaching_pmhigh[relative_gobackdownbelowpmhighafterbreach: ].index[0]

    #print("this is the index of the pmhighdipbelow: ", indexFirstDipDowner)

    # TODO if indexfirstdipdown and indexresbreaker and more than 20 indexes apart (more than 20 min apart), this is not type 1.0 play

    if indexFirstDipDowner - indexFirstResBreaker > 20:
        print('THIS IS NOT A TYPE 1.0 PLAY')

    else:
        isType1PointOhPlay = True

    mymarketafterdippingDF =  market_after_breaching_pmhigh[relative_gobackdownbelowpmhighafterbreach: ]

    AllBelowPmHmymarketafterdippingDF = mymarketafterdippingDF[mymarketafterdippingDF['low'] <= premarket_high]

    mygreensproutdf = AllBelowPmHmymarketafterdippingDF[AllBelowPmHmymarketafterdippingDF['close'] > AllBelowPmHmymarketafterdippingDF['open']] #THIS SHOULD FIND THE TYPE 1.0 GREENSPROUT

    potential_loss = mygreensproutdf[0:1]

    #print()
    #print()
    #print()
    #print("this is poptential loss ", potential_loss['datetime'].values)
    #print()
    #print()
    #print()

    potential_loss_percent = ((potential_loss['high'] - potential_loss['low'])/potential_loss['high']) * 100
    #print("my potential loss is: ", potential_loss_percent, " %")


    buy_price = potential_loss['high'] # stupid variable name but whatever
    stop_loss = potential_loss['low']

    buy_time = potential_loss['datetime']
    #print("THIS IS THE TIME AT WHICH I BOUGHT: ", time.ctime(buy_time/1000))








    #print("disclaimer: it's actually the next candle that I bought at, but the buy price is the high of the candle at the buy time above ")
    #   TODO SO FIND IF IT ACTUALLY MANAGED TO JUMP 15% WITHOUT TRIGGERING THE STOP LOSS. there's no POTENTIAL risk and POTENTIAL gain written here, just what actually happened.
    #    actually yes potential gain should be written. so i can test new take_profits later.
    #print('this is my buy price: ', buy_price)

    try:
        indexOfBuy = buy_price.index.values[0]
    except:
        print("this is the faulty stock because I don't know why: ", stock)
    #print("this is the index of buy:", indexOfBuy)

    # i think just fuck start shimmying in front of the greensprout, checking for any candles that kill the stop, any candles that reach the peak. and this is done uno by uno

    takeProfitLevel = buy_price * 1.15
    #print("this is my take profit level: ",takeProfitLevel)

    #print(marketFri[marketFri['datetime'] > 1602271740000].info())

    try:
        marketAfterMyBuy = marketFri[marketFri['datetime'] > buy_time.values[0]] # 1602271740000 is my buy time
    except:
        print("this is a faulty stock ALSO ALSO because I don't know why: ", stock)
    try:
        indexOfStopLossKiller = marketAfterMyBuy[marketAfterMyBuy['low'] <= stop_loss.values[0]].index.values[0] # never goes below the buy price for ADMP
    except IndexError:
        isStopLossNotReached = True

    try:
        indexOfTakeProfiter = marketAfterMyBuy[marketAfterMyBuy['low'] >= takeProfitLevel.values[0]].index.values[0]
        if indexOfStopLossKiller < indexOfTakeProfiter:
            isWin = True
    except IndexError: # if the takeprofit is never reached
        pass


    if isType1PointOhPlay:
        print("this is the stock: ", stock)
        print("this is my buy time: ", time.ctime(buy_time/1000))
        print("this is my buy price: ", buy_price.values[0])

        if isWin:
            try:
                print('this is the time that my TAKE PROFIT was triggered: ', timeOf(indexOfTakeProfiter))  # TODO if this throws a val error then the 15% was never hit lol
            except ValueError:
                print("Never Reached Take Profit Level")
        else:
            if isStopLossNotReached:
                print("It didn't reach take profit, but didn't kill the stop loss either")
            else:
                print("this was the time my stop loss was triggered: ", timeOf(indexOfStopLossKiller))

        print("================================================")
        print("")
        print("")

    #print('this is my stop loss: ', stop_loss.values[0])
    #print('this is the time that my stop loss was triggered: ', timeOf(indexOfStopLossKiller))

    #print('THIS WAS THE PREMARKET HI:', premarket_high)





    # TODO I WANT TO BE ABLE TO SEARCH FOR THE INDEX OF STOPKILL AND INDEX OF TAKEPROFITREACH AND SEE WHICH COMES FIRST
    '''
    indexOfStopLossKiller = marketAfterMyBuy[marketAfterMyBuy['low'] <= buy_price] # never goes below the buy price for ADMP
    
    print(indexOfStopLossKiller.info())
    
    #print("this is the marketAfterMyBuy: ", marketAfterMyBuy)
    
    #indexOfStopLossKiller = marketAfterMyBuy[marketAfterMyBuy['low']]
    
    
    for i in range(1000):
        print(marketAfterMyBuy[i]['high'])
        if marketAfterMyBuy[i]['high'] >= takeProfitLevel:
            print("I win")
        elif marketAfterMyBuy[i]['low'] <= stop_loss:
            print("I lose")
    
    
    
    
    
    
    highest_day_pt = marketFri["high"].max()
    print("this is the high of the market day", highest_day_pt)
    potential_gain = ((highest_day_pt - potential_loss['high'])/potential_loss['high'])*100
    print("this is my potential gain: ", potential_gain)
    
    
    
    
    
    
    
    mygreensproutdf =  mymarketafterdippingDF[mymarketafterdippingDF['close'] > mymarketafterdippingDF['open'] and mymarketafterdippingDF['low']<=premarket_high]  # finds the first green after the dip back under.
    print(timeOf(mygreensproutdf)) # AND THIS IS WHERE I BUY.
    potential_loss = mygreensproutdf[0:1]
    potential_loss_percent = ((potential_loss['high'] - potential_loss['low'])/potential_loss['high']) * 100
    print("my potential loss is: ", potential_loss_percent, " %")
    
    highest_day_pt = marketFri["high"].max()
    print("this is the high of the market day", highest_day_pt)
    potential_gain = ((highest_day_pt - potential_loss['high'])/potential_loss['high'])*100
    print("this is my potential gain: ", potential_gain)
    #print('NOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO')
    
    
    
    
    
    
    
    print('NOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO'
          ''
          ''
          ''
          ''
          ''
          '')
    to_help_find_market_after_breaking_pmhigh = marketFri[marketFri['high'] >= premarket_high].index.values
    
    print("the time when PM high is broken is: ", time.ctime(to_help_find_market_after_breaking_pmhigh.loc[512]['datetime']/1000)) # find the datetime for the first break of pmhigh
    
    actual_market_after_breaking_pmhigh = marketFri[512:517]
    print(actual_market_after_breaking_pmhigh)
    
    to_help_find_gobelowpmhigh = actual_market_after_breaking_pmhigh[actual_market_after_breaking_pmhigh['low'] <= 3.25]
    
    print(to_help_find_gobelowpmhigh)
    
    '''''