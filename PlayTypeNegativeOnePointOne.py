import requests
import time
import datetime
from datetime import datetime
from TimSort import merge_sort  # merge_sort needs an array

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



def bigloopType4(stock): # Type 1.0 plays


    stock_list = [stock]
    stockCounter = 0  # this is used to advance to the next day whenever algo has checked all the stocks for the current day

    # that means
    # resultsList = [[stock, buy_price, time.ctime(buy_time/1000), isWin, realPercentChange, potentialWinPercentChange]]
    resultsList = [[0, 0, 0, 0, 0, 0, 0]]
    # Create the pandas DataFrame
    resultsTable = pd.DataFrame(resultsList,
                                columns=['Instrument', 'BuyPrice', 'BuyTime', "SellTime", "Win?", "Real%change",
                                         "Potential%Change"])
    '''
    # update all of these later
    # update all of these later
    premarketstart = 1601280000000 #+ 24 * 60 * 60 * 1000 # 28th sept 4PM SGT,

    currentTime = 1601251200000 #+ 24 * 60 * 60 * 1000 # 28th sept 8AM SGT
    endTime = 1603324800000 + 24 * 60 * 60 * 1000*-22  # 30th Sept 8AM SGT
#+ 24 * 60 * 60 * 1000 * 10
    '''
    startDateString = "5/11/2020 08:00:00"
    premarketStartDateString = "5/11/2020 17:00:00"
    endDateString = "28/11/2020 22:00:00"
    currentTime = int((datetime.timestamp(
        datetime.strptime(startDateString, "%d/%m/%Y %H:%M:%S"))) * 1000)
    premarketstart = int((datetime.timestamp(
        datetime.strptime(premarketStartDateString, "%d/%m/%Y %H:%M:%S"))) * 1000)
    endTime = int((datetime.timestamp(
        datetime.strptime(endDateString, "%d/%m/%Y %H:%M:%S"))) * 1000)



    stockIterator = 0

    counter = 0
    while(counter < 1):
        counter = 1

        if stockIterator == len(stock_list):
            print(" we are moving to the next day now ")
            stockIterator = 0 # we have reached the end of the stock list, reset the stockIterator to 0 so we can start afresh, and progress to a new day
            premarketstart = premarketstart + 24 * 60 * 60 * 1000
            currentTime = currentTime +  24 * 60 * 60 * 1000

        stock = stock_list[stockIterator]
        stockIterator = stockIterator + 1
        print("this is the current time variable's value, ", time.ctime(currentTime / 1000))
        print("this is the stockIterator, ", stockIterator)
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

        premarketend = premarketstart + (5 * 60 * 60 + 29 * 60) * 1000 #+ 25*60*60*1000 # TODO idk why I had to add 25 more hours.

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

        redSproutLow = 0
        redSproutHigh = 0







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

        currentDate = df['Date'].values[0]
        currentFuckingTime = df['24HTime'].values[0]
        print("this is the current date:, " ,currentDate)

        print("this is the current time: ", currentFuckingTime )

        print("this is the end time: ", time.ctime(endTime/1000))

        premarketFri_start = df[df['datetime'] >= premarketstart]


        premarketFri = premarketFri_start[premarketFri_start['datetime'] <= premarketend]
        #print(time.ctime(premarketend/1000), premarketFri_start)

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
        print("this is the premarket start", datetime.fromtimestamp(premarketstart/ 1000).strftime('%H%M %d-%m-%Y'))
        print(premarketFri_start)

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

        #print(index_of_go_back_above_pm_low_after_crack)


        index_of_market_after_cracking_pmlowStart = market_after_cracking_pmlow.index[0]



        relative_go_back_above_pm_low_after_crack = index_of_go_back_above_pm_low_after_crack - index_of_market_after_cracking_pmlowStart

        indexFirstThrustUpper = market_after_cracking_pmlow[relative_go_back_above_pm_low_after_crack:].index[0]




        # TODO if indexfirstdipdown and indexresbreaker and more than 20 indexes apart (more than 20 min apart), this is not type 1.0 play

        if indexFirstThrustUpper - indexFirstSupportCracker > 20:
            print('THIS IS NOT A TYPE -1.0 PLAY because it took too long to re-go-above-the-support, for stock name: ', stock)
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
            redSproutLow = shortSellPrice
        except:
            print("getting the shortSellPrice fucked up, the offending stock is, ", stock)

        try:
            stop_loss = potential_loss['high'].values[0]
            redSproutHigh = stop_loss
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
        return [redSproutHigh, redSproutLow]


    resultsTable.to_excel(r'C:\Users\rohit kurup\Documents\PlayType-1Point1(2ndNovTo20thNov2020)(StocksFrom21stTo25thSept)Test2.xlsx', index=False, header=True)




#bigloopType4()