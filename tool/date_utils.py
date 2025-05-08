import datetime
import random

def generate_dates(start_date_str, end_date_str):
    """Generates a list of dates between start_date and end_date with random intervals.

    Args:
        start_date_str (str): The start date in YYYY-MM-DD format.
        end_date_str (str): The end date in YYYY-MM-DD format.

    Returns:
        list[datetime.date]: A list of date objects.
    """
    try:
        start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d").date()
        end_date = datetime.datetime.strptime(end_date_str, "%Y-%m-%d").date()
    except ValueError as e:
        raise ValueError(f"Invalid date format. Please use YYYY-MM-DD. Error: {e}")

    if start_date > end_date:
        raise ValueError("Start date cannot be after end date.")

    dates = []
    current_date = start_date
    while current_date <= end_date:
        dates.append(current_date)
        # Generate a random interval between 1 and 5 days
        days_increment = random.randint(1, 5)
        current_date += datetime.timedelta(days=days_increment)
    
    return dates

if __name__ == "__main__":
    # Example usage:
    try:
        # Test case 1: Valid date range
        start = "2024-01-01"
        end = "2024-01-15"
        generated_dates = generate_dates(start, end)
        print(f"Generated dates between {start} and {end}:")
        for date_obj in generated_dates:
            print(date_obj.strftime("%Y-%m-%d"))
        print("-"*20)

        # Test case 2: Start date is the same as end date
        start_same = "2024-02-10"
        end_same = "2024-02-10"
        generated_dates_same = generate_dates(start_same, end_same)
        print(f"Generated dates between {start_same} and {end_same}:")
        for date_obj in generated_dates_same:
            print(date_obj.strftime("%Y-%m-%d"))
        print("-"*20)

        # Test case 3: Date range spanning across months
        start_month = "2024-03-25"
        end_month = "2024-04-05"
        generated_dates_month = generate_dates(start_month, end_month)
        print(f"Generated dates between {start_month} and {end_month}:")
        for date_obj in generated_dates_month:
            print(date_obj.strftime("%Y-%m-%d"))
        print("-"*20)

        # Test case 4: Invalid date format (should raise ValueError)
        # start_invalid_format = "01-01-2024"
        # end_invalid_format = "2024-01-15"
        # print(f"Testing invalid format {start_invalid_format} to {end_invalid_format}:")
        # generate_dates(start_invalid_format, end_invalid_format)

        # Test case 5: Start date after end date (should raise ValueError)
        # start_after_end = "2024-01-15"
        # end_after_end = "2024-01-01"
        # print(f"Testing start date after end date {start_after_end} to {end_after_end}:")
        # generate_dates(start_after_end, end_after_end)

    except ValueError as e:
        print(f"Error: {e}") 