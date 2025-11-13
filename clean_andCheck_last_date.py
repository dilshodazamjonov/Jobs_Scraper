import re
from datetime import datetime

def clean_and_check_date(input_string):
    """
    Extracts the first date from the input string and checks if it matches the current date.
    :param input_string: str - The input containing the date.
    :return: bool - True if the date matches the current date, False otherwise.
    """
    try:
        # Extract potential dates using regex
        date_matches = re.findall(r'\d{2,4}[./-]\d{2}[./-]\d{2}', input_string)

        if not date_matches:
            raise ValueError("No valid date found in the input.")

        # Process the first date match
        raw_date = date_matches[0]
        # print(f"Matched Date: {raw_date}")  # Debugging

        # Parse the date, considering its format
        if len(raw_date.split('/')[0]) == 2:  # YY/MM/DD format
            parsed_date = datetime.strptime(raw_date, "%y/%m/%d")
        elif '.' in raw_date:  # YYYY.MM.DD format
            parsed_date = datetime.strptime(raw_date, "%Y.%m.%d")
        elif '-' in raw_date:  # YYYY-MM-DD format
            parsed_date = datetime.strptime(raw_date, "%Y-%m-%d")
        else:
            raise ValueError("Unexpected date format.")

        # Get the current date
        current_date = datetime.now().strftime("%m/%d/%Y")
        extracted_date = parsed_date.strftime("%m/%d/%Y")

        # Compare extracted date with current date
        return extracted_date == current_date

    except Exception as e:
        print(f"Error: {e}")
        return False

