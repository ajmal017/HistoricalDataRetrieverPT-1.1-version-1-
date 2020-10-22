import requests
import time
import datetime
from datetime import datetime
from TimSort import merge_sort  # merge_sort needs an array
from main import stock_set
import pandas as pd
import warnings
import openpyxl
import numpy as np

warnings.filterwarnings("ignore")
key = 'ARJTRG5ZQH4Y6MWQJLA0LLHUZVZBU21S'




# TODO some caveats to add
# TODO the code is buggy go fix it.
# TODO make it that the risk is always kept below the base of the last green. NOW NOW NOW.
# TODO then try w 5 min candles instead
# todo try to do this by modifying table itself, the stop loss should be unable to be killed if it's not the last known green



def bigloopType3(): # Type 1.0 plays
    stock_list = list(stock_set)
    #stock_list = ["SOL"]
    stockCounter = 0  # this is used to advance to the next day whenever algo has checked all the stocks for the current day

    # that means
    # resultsList = [[stock, buy_price, time.ctime(buy_time/1000), isWin, realPercentChange, potentialWinPercentChange]]
    resultsList = [[0, 0, 0, 0, 0, 0, 0]]
    # Create the pandas DataFrame
    resultsTable = pd.DataFrame(resultsList,
                                columns=['Instrument', 'BuyPrice', 'BuyTime', "SellTime", "Win?", "Real%change",
                                         "Potential%Change"])

    # update all of these later
    premarketstart = 1603094400000+ 24 * 60 * 60 * 1000*2# 21th oct 4PM SGT,



    currentTime = 1603065600000+ 24 * 60 * 60 * 1000*2 #21th OCT 8AM SGT
    endTime = 1603262952000+ 24 * 60 * 60 * 1000# 22nd OCT 8AM SGT
#+ 24 * 60 * 60 * 1000 * 10
    stockIterator = 0


    while(currentTime < endTime):

        if stockIterator == len(stock_list):
            stockIterator = 0 # we have reached the end of the stock list, reset the stockIterator to 0 so we can start afresh, and progress to a new day
            premarketstart = premarketstart + 24 * 60 * 60 * 1000
            currentTime = currentTime +  24 * 60 * 60 * 1000
        stock = stock_list[stockIterator]
        stockIterator = stockIterator + 1
        # start_date_string = "10/06/2020 04:00:00"
        # end_date_string = "10/06/2020 09:29:00"
        multiplier = 0.94  # this is where I'll take profit
        # Considering date is in dd/mm/yyyy format
        # start_date  = datetime.timestamp(datetime.strptime(start_date_string, "%m/%d/%Y %H:%M:%S"))*1000
        # end_date = datetime.timestamp(datetime.strptime(end_date_string, "%m/%d/%Y %H:%M:%S"))*1000
        # 512 is first index val

        isTakeProfitReached = False  # false by default
        isType1PointOhPlay = False
        isWin = False
        isStopLossNotReached = False

        doesTakeProfitLevelExist = False  # Note that this is used to see if the level is ever reached, but the stop loss might actually be killed first
        doesStopLossKillerExist = False

        doGreensBelowPMHighExist = False  # these refer to greens after the first resistance break

        premarketend = premarketstart + (5 * 60 * 60 + 29 * 60) * 1000

        marketopen = premarketstart + (5 * 60 * 60 + 30 * 60) * 1000
        marketclose = premarketstart + (12 * 60 * 60) * 1000

        timeOfSale = 0

        realPercentChange = 0  # this is how much I actually increased or decreased
        potentialWinPercentChange = 0  # this is the percentage INCREASE that I could have made

        def convertTimeTo24H(time):
            return datetime.fromtimestamp(time / 1000).strftime('%Y-%m-%d %H%M')

        def getPriceHistory(**kwargs):

            url = 'https://api.tdameritrade.com/v1/marketdata/{}/pricehistory'.format(kwargs.get('symbol'))
            params = {}
            params.update({'apikey': key})

            for arg in kwargs:
                parameter = {arg: kwargs.get(arg)}
                params.update(parameter)

            return requests.get(url, params=params).json()

        def timeOf(dataframe):  # we assume that we're passed the dataframe. you pass this a whole fat dataframe
            try:
                return time.ctime(dataframe['datetime'].min() / 1000)
            except:
                print("this is the faulty stock regarding the timeOf function: ", stock)
                print("================================================")
                print("")
                print("")

        def findPercentageChange(before, after):
            if after > before:
                return ((after - before) / before) * 100
            else:
                return ((after - before) / before) * 100

        def doesPriceLevelExist(df, col, price,
                                condition):  # helps you see if a price level exists for a given condition
            # df is a dataframe. col is a column in df, string type. price is an int.
            if condition == 'greateroreq':
                return (df[col].values >= price).any()
            if condition == 'greater':
                return (df[col].values > price).any()
            if condition == 'lessoreq':
                return (df[col].values <= price).any()
            if condition == 'lesser':
                return (df[col].values < price).any()

        def time24HOfIncident(
                df):  # helps you see the 24Htime of an incident occurring. Pass this a full dataframe (with conditional), it takes the 24HTime of the first index.
            return df['24HTime'].values[0]

        try:
            friendly_dict = getPriceHistory(symbol=stock, periodType='day', frequencyType='minute',
                                            startDate=currentTime, endDate=endTime, needExtendedHoursData=True)
            #print(friendly_dict)

        except:
            print("this stock does not exist: ", stock)
            print("================================================")
            print("")
            print("")
            continue

        try:
            df = pd.DataFrame(friendly_dict['candles'])
        except:
            print("can't get the candles from friendly dict for this stock, ", stock)
        if len(df) == 0:
            print("This stock does not exist, ", stock)
            print("================================================")
            print("")
            print("")
            continue


        df['24HTime'] = df.apply(lambda row: datetime.fromtimestamp(row.datetime / 1000).strftime('%H%M'), axis=1)
        df['Date'] = df.apply(lambda row: datetime.fromtimestamp(row.datetime / 1000).strftime('%d-%m-%Y'), axis=1)



        premarketFri_start = df[df['datetime'] >= premarketstart]


        premarketFri = premarketFri_start[premarketFri_start['datetime'] <= premarketend]
        #print(premarketend)

        marketFri_start = df[df['datetime'] >= marketopen]
        marketFri = marketFri_start[marketFri_start['datetime'] <= marketclose]
        premarket_low = premarketFri['low'].min()

        if premarket_low < 0:  # changed from $6 to be all inclusive
            print("Stock is too cheap: ", stock)
            print("================================================")
            print("")
            print("")
            continue
        print('this is the premarket low', premarket_low)


        #try:
        if doesPriceLevelExist(marketFri, 'low', premarket_low, 'lesser'):
            print("for ", stock,  doesPriceLevelExist(marketFri, 'low', premarket_low, 'lesser'))
            indexFirstSupportCracker = marketFri[marketFri['low'].lt(premarket_low)].index[0]
        else:
            print("this stock doesn't crack the premarket low: ", stock)
            print("================================================")
            print("")
            print("")
            continue


        index_of_breach = marketFri[marketFri['low'].lt(premarket_low)].index[0]

        #print(marketFri.loc[index_of_breach])


        index_of_marketFriStart = marketFri.index[0]

        relative_index_of_breach = index_of_breach - index_of_marketFriStart

        market_after_cracking_pmlow = marketFri[relative_index_of_breach + 1:]  # ignores the first breaking candle


        try:
            index_of_go_back_above_pm_low_after_crack = \
            market_after_cracking_pmlow[market_after_cracking_pmlow['high'].gt(premarket_low)].index[0]
        except:
            print("this is the faulty stock because it doesn't go up again after cracking the support: ", stock)
            print("================================================")
            print("")
            print("")
            continue

        print(index_of_go_back_above_pm_low_after_crack)


        index_of_market_after_cracking_pmlowStart = market_after_cracking_pmlow.index[0]



        relative_go_back_above_pm_low_after_crack = index_of_go_back_above_pm_low_after_crack - index_of_market_after_cracking_pmlowStart

        indexFirstThrustUpper = market_after_cracking_pmlow[relative_go_back_above_pm_low_after_crack:].index[0]

        #print(market_after_cracking_pmlow.loc[indexFirstThrustUpper])


        # TODO if indexfirstdipdown and indexresbreaker and more than 20 indexes apart (more than 20 min apart), this is not type 1.0 play

        if indexFirstThrustUpper - indexFirstSupportCracker > 20:
            print('THIS IS NOT A TYPE -1.0 PLAY, for stock name: ', stock)
            print("================================================")
            print("")
            print("")
            continue

        else:
            isType1PointOhPlay = True


        mymarketafterthrustingDF = market_after_cracking_pmlow[relative_go_back_above_pm_low_after_crack:]

        AllAbovePmLmymarketafterthrustingDF = mymarketafterthrustingDF[mymarketafterthrustingDF['high'] >= premarket_low]





        if (AllAbovePmLmymarketafterthrustingDF['open'] > AllAbovePmLmymarketafterthrustingDF[
            'close']).any():  # if there are any reds present in the thrust portion after the PMLowCrack --- rephrased for type -1.0
            doRedsAbovePMLowExist = True
            myredsproutdf = AllAbovePmLmymarketafterthrustingDF[
                AllAbovePmLmymarketafterthrustingDF['open'] > AllAbovePmLmymarketafterthrustingDF['close']]
        else:
            print("There are no reds present in the thrust portion after the PMLowCrack: ", stock)
            print("================================================")
            print("")
            print("")
            continue



        potential_loss = myredsproutdf[0:1]

        #print(potential_loss)

        potential_loss_percent = ((potential_loss['low'] - potential_loss['high']) / potential_loss['low']) * 100

        try:
            shortSellPrice = potential_loss['low'].values[0]
        except:
            print("getting the shortSellPrice fucked up, the offending stock is, ", stock)

        try:
            stop_loss = potential_loss['high'].values[0]
        except:
            print("I can't get the stop loss for this stock: ", stock)

        if doRedsAbovePMLowExist:
            shortSellTime = potential_loss['datetime'].values[0]

        try:
            indexOfShortSell = potential_loss['low'].index.values[0]
        except:
            print("this is the faulty stock because I think because it doesnt have a ShortSell price but pls check: ", stock)
            print("================================================")
            print("")
            print("")
            continue

        takeProfitLevel = shortSellPrice * multiplier

        marketAfterMyBuy = marketFri[marketFri['datetime'] > shortSellTime]  # 1602271740000 is my buy time.
        # NOTE THAT THE CANDLE I BUY ON IS ONE IN FRONT OF THE CONFIRMATION REDSPROUT CANDLE



        doesTakeProfitLevelExist = doesPriceLevelExist(marketAfterMyBuy, 'low', takeProfitLevel, 'lessoreq')
        doesStopLossKillerExist = doesPriceLevelExist(marketAfterMyBuy, 'high', stop_loss, 'greateroreq')

        #

        # if they both exist, then I want to find out which came first so i know if i won or loss
        if doesStopLossKillerExist and doesTakeProfitLevelExist:
            timeOfTakeProfit = marketAfterMyBuy[marketAfterMyBuy['low'] <= takeProfitLevel]['datetime'].values[0]
            timeOfStopLossKiller = marketAfterMyBuy[marketAfterMyBuy['high'] >= stop_loss]['datetime'].values[0]
            if timeOfTakeProfit < timeOfStopLossKiller:
                print("I won, I bought to cover at: ",
                      time24HOfIncident(marketAfterMyBuy[marketAfterMyBuy['low'] <= takeProfitLevel]))

                realPercentChange = findPercentageChange(shortSellPrice, takeProfitLevel)
                timeOfSale = time24HOfIncident(marketAfterMyBuy[marketAfterMyBuy['low'] <= takeProfitLevel])

            else:
                marketFromBuyToStopLossBuyCover = marketAfterMyBuy.loc[
                    (((marketAfterMyBuy['datetime'] > shortSellTime) & (
                                marketAfterMyBuy['datetime'] < timeOfStopLossKiller)))]
                lowestPointReachedBeforeBuyingToCover = marketFromBuyToStopLossBuyCover['low'].min()

                print("I lost, I bought to cover at: ", time24HOfIncident(marketAfterMyBuy[marketAfterMyBuy['high'] >= stop_loss]),
                      " but before I died the highest ($ not %change) point was at: ", lowestPointReachedBeforeBuyingToCover)
                realPercentChange = findPercentageChange(shortSellPrice, stop_loss)
                potentialWinPercentChange = findPercentageChange(shortSellPrice, lowestPointReachedBeforeBuyingToCover)
                timeOfSale = time24HOfIncident(marketAfterMyBuy[marketAfterMyBuy['high'] >= stop_loss])

        # # if one of them exists, take it either as a loss or win
        if doesTakeProfitLevelExist and not doesStopLossKillerExist:
            print("I won, I sold at: ",
                  time24HOfIncident(marketAfterMyBuy[marketAfterMyBuy['low'] <= takeProfitLevel]))
            realPercentChange = findPercentageChange(shortSellPrice, takeProfitLevel)
            timeOfSale = time24HOfIncident(marketAfterMyBuy[marketAfterMyBuy['low'] <= takeProfitLevel])
        elif doesStopLossKillerExist and not doesTakeProfitLevelExist:
            timeOfStopLossKiller = marketAfterMyBuy[marketAfterMyBuy['high'] >= stop_loss]['datetime'].values[0]
            marketFromBuyToStopLossBuyCover = marketAfterMyBuy.loc[
                (((marketAfterMyBuy['datetime'] > shortSellTime) & (marketAfterMyBuy['datetime'] < timeOfStopLossKiller)))]
            lowestPointReachedBeforeBuyingToCover = marketFromBuyToStopLossBuyCover['low'].min()

            print("I lost, I bought to cover at: ", time24HOfIncident(marketAfterMyBuy[marketAfterMyBuy['high'] >= stop_loss]),
                  " but before I died the highest ($ not %change) point was at: ",lowestPointReachedBeforeBuyingToCover)
            realPercentChange = findPercentageChange(shortSellPrice, stop_loss)
            potentialWinPercentChange = findPercentageChange(shortSellPrice, lowestPointReachedBeforeBuyingToCover)
            timeOfSale = time24HOfIncident(marketAfterMyBuy[marketAfterMyBuy['high'] >= stop_loss])

        # if they both DON'T exist, find the highest point reached
        if not doesTakeProfitLevelExist and isStopLossNotReached:
            print("I neither won nor lost, the highest ($ not %change) point reached was: ",
                  marketAfterMyBuy['high'].max(), " and the percentage change was, ",
                  findPercentageChange(shortSellPrice, marketAfterMyBuy['low'].min()))
            potentialWinPercentChange = findPercentageChange(shortSellPrice, lowestPointReachedBeforeBuyingToCover)

        try:
            timeOfStopLossKiller = marketAfterMyBuy[marketAfterMyBuy['high'] >= stop_loss]['datetime'].values[0]
        except:
            print("I couldn't get the time of stop loss killer, offending stock is: ", stock)

        new_row = {'Instrument': stock, 'BuyPrice': shortSellPrice, 'BuyTime': time.ctime(shortSellTime / 1000),
                   "SellTime": timeOfSale, "Win?": isWin, "Real%change": realPercentChange,
                   "Potential%Change": potentialWinPercentChange}
        # append row to the dataframe
        resultsTable = resultsTable.append(new_row, ignore_index=True)

        isStopLossNotReached = True  # TODO yeah this is floating around after i deleted the try catch block, find a good place to put it

        # todo here we start the main deal
        if isType1PointOhPlay:
            print("this is the stock: ", stock, " the stock is: ", stock)
            print("this is my SHORTSELL time: ", time.ctime(shortSellTime / 1000), " the stock is: ", stock)
            print("this is my SHORTSELL price: ", shortSellPrice, " the stock is: ", stock, " and the premarket low was, ",
                  premarket_low)
            print("was this a win for", stock, " ?: ", isWin)
            print("================================================")
            print("")
            print("")

        # TODO I WANT TO BE ABLE TO SEARCH FOR THE INDEX OF STOPKILL AND INDEX OF TAKEPROFITREACH AND SEE WHICH COMES FIRST

    resultsTable.to_excel(r'C:\Users\rohit kurup\Documents\ukn', index=False, header=True)




bigloopType3()