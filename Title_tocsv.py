import pandas as pd
import os

def to_csv(titles: list, file_name: str = "Title.csv"):
    df = pd.DataFrame({"Title": titles})
    
    # Append if file exists, else create
    if os.path.exists(file_name):
        df.to_csv(file_name, mode='a', header=False, index=False)
    else:
        df.to_csv(file_name, index=False)
    
    print(f"File '{file_name}' updated with {len(titles)} titles.")
