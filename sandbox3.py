# import datetime
from datetime import datetime
import time



dt_string = "06/10/2020 16:00:32"
dt_string2 = "06/10/2020 21:29:32"
# Considering date is in dd/mm/yyyy format
dt_object1 = datetime.strptime(dt_string, "%d/%m/%Y %H:%M:%S")
dt_object2 = datetime.strptime(dt_string2, "%d/%m/%Y %H:%M:%S")

# Convert dt_object2 to Unix Timestamp
start_timestamp = datetime.timestamp(dt_object1)
end_timestamp = datetime.timestamp(dt_object2)
print('Unix Timestamp for START date: ', start_timestamp)
print('Unix Timestamp for END  date: ', end_timestamp)
#current_time = time.time()
#print(int(((current_time - timestamp)/3600)/24))