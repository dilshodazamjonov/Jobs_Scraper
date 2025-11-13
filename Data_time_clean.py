import re
from datetime import datetime

def clean_and_format_first_date(input_string):
    """
    Extracts the first date from the input string and formats it to MM/DD/YYYY.
    Handles dates in formats: YYYY.MM.DD, YYYY/MM/DD, YYYY-MM-DD.
    :param input_string: str - The input containing the date.
    :return: str - The formatted date in MM/DD/YYYY, or None if no valid date is found.
    """
    try:
        # Match YYYY.MM.DD, YYYY/MM/DD, YYYY-MM-DD
        date_matches = re.findall(r'\d{4}[./-]\d{2}[./-]\d{2}', input_string)

        if not date_matches:
            raise ValueError("Could not find a valid date in the input.")

        # Replace any separator with '.' for consistent parsing
        raw_date = date_matches[0].replace('-', '.').replace('/', '.')

        formatted_date = datetime.strptime(raw_date, "%Y.%m.%d").strftime("%m/%d/%Y")
        return formatted_date

    except Exception as e:
        print(f"Error: {e}")
        return None
