
import pytz
from pytz import timezone
import sys
from datetime import datetime

if __name__ == "__main__":
    

    if sys.argv[1]=="-s":
        local_tz = pytz.timezone('America/Los_Angeles')
        # get the current time in the local timezone
        now = datetime.now()

        # convert the local time to UTC
        utc_now = now.astimezone(pytz.utc)

        # print the UTC time in ISO format
        print(utc_now.isoformat())

    elif sys.argv[1]=="-c":

        # get the current time in the local timezone
        now = datetime.now()

        # convert the local time to UTC
        utc_now = now.astimezone(pytz.utc)

        # print the UTC time in ISO format
        print(utc_now.isoformat())