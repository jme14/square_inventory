from datetime import datetime, timedelta

"""  
DATE STUFF 
"""
def get_dates_from_date_file():
    with open("dates.txt", "r") as file:
        open_date_string = file.readline().strip()
        close_date_string = file.readline().strip()
        try:
            open_date = datetime.strptime(open_date_string, "%Y-%m-%d")
            close_date = datetime.strptime(close_date_string, "%Y-%m-%d")
            return open_date, close_date
        except ValueError as e:
            print("ERROR: format the dates in YYYY-MM-DD format in each row")
            return None, None

# translates to square recognizable datetime from timezone nonsense 
def get_open_close_time(open_datetime, close_datetime):
    return (open_datetime+timedelta(hours=7)+timedelta(hours=8), close_datetime+timedelta(hours=7)+timedelta(hours=26))