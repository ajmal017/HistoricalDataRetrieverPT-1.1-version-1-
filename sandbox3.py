# import datetime
from datetime import datetime
import time

# be able to convert, using a function, ms to 24 hour time.
# that's gonna be used as the index to replace the regular index in the thinkorswim helper thing, and then that's gonna make things easier pour moi

'''
dt_string = "1600" # on friday october 9th # and this is gonna be converted into the ms thing similar to what the thinkorswim thing returns
dt_string2 = "2129"
# Considering date is in dd/mm/yyyy format
dt_object1 = datetime.strptime(dt_string, "%H:%M:%S")
dt_object2 = datetime.strptime(dt_string2, "%d/%m/%Y %H:%M:%S")
'''

# TODO premarket start Friday Oct 9th = 1602230400000


# wait as in, convert ms to that

from datetime import datetime
ts = int("1602172800")

# if you encounter a "year is out of range" error the timestamp
# may be in milliseconds, try `ts /= 1000` in that case
print(datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H%M'))

def convertTimeTo24H(time):
    return datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H%M')

# Convert dt_object2 to Unix Timestamp
#start_timestamp = datetime.timestamp(dt_object1)
#end_timestamp = datetime.timestamp(dt_object2)
##print('Unix Timestamp for START date: ', start_timestamp)
#print('Unix Timestamp for END  date: ', end_timestamp)
#current_time = time.time()
#print(int(((current_time - timestamp)/3600)/24))