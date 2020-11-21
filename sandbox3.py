# I want to be able to just write down like 21112020, that means 21st NOV 2020 then i get the PREMARKET START, CURRENT TIME AND END TIME
# CURRENT TIME WILL BE 8AM SGT
# PREMARKET START TIME WILL BE 5PM SGT (SINCE DAYLIGHT SAVING LOL)
from datetime import datetime
startDateString = "02/11/2020 08:00:00"
premarketStartDateString = "02/11/2020 17:00:00"
endDateString = "20/11/2020 22:00:00"
subtractToNYTimeWDaylightSavings = 13*60*60
start_date  = int((datetime.timestamp(datetime.strptime(startDateString, "%d/%m/%Y %H:%M:%S")) - subtractToNYTimeWDaylightSavings )*1000)
premarketStartDate = int((datetime.timestamp(datetime.strptime(premarketStartDateString, "%d/%m/%Y %H:%M:%S")) - subtractToNYTimeWDaylightSavings )*1000)
endDate = int((datetime.timestamp(datetime.strptime(endDateString, "%d/%m/%Y %H:%M:%S")) - subtractToNYTimeWDaylightSavings )*1000)
print(start_date)
