import pandas as pd
import os

def to_csv(titles: list, file_name: str = "Title.csv"):
    """
    Save a list of AI-matched job titles to a CSV file.
    Overwrites the file if it already exists.
    """
    # Create a DataFrame
    df = pd.DataFrame({"Title": titles})
    
    # Write to CSV (overwrite if exists)
    df.to_csv(file_name, index=False)
    
    print(f"File '{file_name}' has been created/overwritten with {len(titles)} titles.")
