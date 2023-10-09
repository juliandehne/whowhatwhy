from datetime import datetime, timedelta

import pytz


def next_8am_berlin(hour=8):
    # Get the current time in Berlin
    berlin = pytz.timezone('Europe/Berlin')
    now = datetime.now(berlin)

    # Check if the current time is already past 8 am
    if now.hour >= hour:
        # If it's past 8 am, go to the next day
        next_date = now + timedelta(days=1)
    else:
        # If it's before 8 am, use the current date
        next_date = now

    # Set the time to 8 am
    eight_am = next_date.replace(hour=hour, minute=0, second=0, microsecond=0)
    return eight_am
