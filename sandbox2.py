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
            print("this is the faulty stock regarding the timeOf function: ", stock)
            print("================================================")
            print("")
            print("")


    try:
        friendly_dict = getPriceHistory(symbol=stock, periodType='day', frequencyType='minute', startDate = 1602172800000, endDate = 1602450000000, needExtendedHoursData = True)
    except:
        print("this stock does not exist: ", stock)
        print("================================================")
        print("")
        print("")
        continue


    df = pd.DataFrame(friendly_dict['candles'])
    try:
        premarketFri_start = df[df['datetime'] >= 1602230400000]
        premarketFri = premarketFri_start[premarketFri_start['datetime'] <= 1602250140000]
        marketFri_start = df[df['datetime'] >= 1602250200000]
        marketFri = marketFri_start[marketFri_start['datetime'] <= 1602273600000]
    except:
        print("this stock is a problem but no idea why: ", stock)
        print("================================================")
        print("")
        print("")
        continue




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
        print("================================================")
        print("")
        print("")
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
        print("================================================")
        print("")
        print("")
        continue

    index_of_market_after_breaching_pmhighStart = market_after_breaching_pmhigh.index[0]
    relative_gobackdownbelowpmhighafterbreach = index_of_gobackdownbelowpmhighafterbreach - index_of_market_after_breaching_pmhighStart

    indexFirstDipDowner = market_after_breaching_pmhigh[relative_gobackdownbelowpmhighafterbreach: ].index[0]


    # TODO if indexfirstdipdown and indexresbreaker and more than 20 indexes apart (more than 20 min apart), this is not type 1.0 play

    if indexFirstDipDowner - indexFirstResBreaker > 20:
        print('THIS IS NOT A TYPE 1.0 PLAY, for stock name: ', stock)
        print("================================================")
        print("")
        print("")
        continue

    else:
        isType1PointOhPlay = True

    mymarketafterdippingDF =  market_after_breaching_pmhigh[relative_gobackdownbelowpmhighafterbreach: ]

    AllBelowPmHmymarketafterdippingDF = mymarketafterdippingDF[mymarketafterdippingDF['low'] <= premarket_high]

    mygreensproutdf = AllBelowPmHmymarketafterdippingDF[AllBelowPmHmymarketafterdippingDF['close'] > AllBelowPmHmymarketafterdippingDF['open']] #THIS SHOULD FIND THE TYPE 1.0 GREENSPROUT

    potential_loss = mygreensproutdf[0:1]



    potential_loss_percent = ((potential_loss['high'] - potential_loss['low'])/potential_loss['high']) * 100



    buy_price = potential_loss['high'] # stupid variable name but whatever
    stop_loss = potential_loss['low']

    buy_time = potential_loss['datetime']
    #print("THIS IS THE TIME AT WHICH I BOUGHT: ", time.ctime(buy_time/1000))








    #print("disclaimer: it's actually the next candle that I bought at, but the buy price is the high of the candle at the buy time above ")

    try:
        indexOfBuy = buy_price.index.values[0]
    except:
        print("this is the faulty stock because I think because it doesnt have a buy price but pls check: ", stock)
        print("================================================")
        print("")
        print("")
        continue
    #print("this is the index of buy:", indexOfBuy)

    # i think just fuck start shimmying in front of the greensprout, checking for any candles that kill the stop, any candles that reach the peak. and this is done uno by uno

    takeProfitLevel = buy_price * 1.15
    #print("this is my take profit level: ",takeProfitLevel)

    #print(marketFri[marketFri['datetime'] > 1602271740000].info())

    try:
        marketAfterMyBuy = marketFri[marketFri['datetime'] > buy_time.values[0]] # 1602271740000 is my buy time
    except:
        print("this is a faulty stock ALSO ALSO because I don't know why: ", stock)
        print("================================================")
        print("")
        print("")
        continue

    try:
        indexOfStopLossKiller = marketAfterMyBuy[marketAfterMyBuy['low'] <= stop_loss.values[0]].index.values[0] # never goes below the buy price for ADMP
        marketAfterBuyRiseThenFallToStopLoss = marketAfterMyBuy[marketAfterMyBuy.index.values[0] < indexOfStopLossKiller] # TODO find out how the fuck to slice
        highest_point_reached = marketAfterBuyRiseThenFallToStopLoss['high'].max()
    except IndexError:
        isStopLossNotReached = True
        highest_point_reached = marketAfterMyBuy['high'].max()
    try:
        indexOfTakeProfiter = marketAfterMyBuy[marketAfterMyBuy['low'] >= takeProfitLevel.values[0]].index.values[0]
        if indexOfStopLossKiller < indexOfTakeProfiter:
            isWin = True
    except: # if the takeprofit is never reached
        pass

# todo here we start the main deal
    if isType1PointOhPlay:
        print("this is the stock: ", stock, " the stock is: ", stock)
        print("this is my buy time: ", time.ctime(buy_time/1000), " the stock is: ", stock)
        print("this is my buy price: ", buy_price.values[0], " the stock is: ", stock, " and the premarket high was, ", premarket_high)
        print("was this a win for", stock, " ?: ", isWin)
        print("the highest percentage gain after my buy without triggering take profit or stop loss was ",((highest_point_reached/buy_price) - 1)*100)
        if isWin:
            try:
                print('this is the time that my TAKE PROFIT was triggered: ', timeOf(indexOfTakeProfiter), " the stock is: ", stock)  # TODO if this throws a val error then the 15% was never hit lol
            except ValueError:
                print("Never Reached Take Profit Level", " the stock is: ", stock)
        else:
            if isStopLossNotReached:
                print("It didn't reach take profit, but didn't kill the stop loss either", " the stock is: ", stock)
            else:
                print("this was the time my stop loss was triggered: ", timeOf(indexOfStopLossKiller), " the stock is: ", stock)

        print("================================================")
        print("")
        print("")

    #print('this is my stop loss: ', stop_loss.values[0])
    #print('this is the time that my stop loss was triggered: ', timeOf(indexOfStopLossKiller))

    #print('THIS WAS THE PREMARKET HI:', premarket_high)





    # TODO I WANT TO BE ABLE TO SEARCH FOR THE INDEX OF STOPKILL AND INDEX OF TAKEPROFITREACH AND SEE WHICH COMES FIRST
