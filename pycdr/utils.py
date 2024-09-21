from typing import List
from datetime import timedelta


def generate_date_range(start:str, end:str, freq=1) -> List[str]:
    """
    Generate a list of dates within the specified range.
    
    Args:
        start (str): The start date in 'YYYY-MM-DD' format.
        end (str): The end date in 'YYYY-MM-DD' format.
        freq (str, optional): The frequency of dates. Defaults to '1D' (daily).

    Returns:
        List[str]: A list of date strings in 'YYYYMMDD' format.
    """
    dates_period = []
    current_date = start
    while current_date <= end:
        dates_period.append(current_date.strftime('%Y%m%d'))
        current_date += timedelta(days=freq)
    return dates_period