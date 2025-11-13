import pandas as pd
import os
import glob
import shutil

def collect_csv():
    folder_path = "data"
    output_file = "combined_output.csv"

    # Check if the folder exists
    if not os.path.exists(folder_path):
        print(f"Folder '{folder_path}' does not exist. Please provide a valid path.")
        return

    # Get all CSV files in the folder
    csv_files = glob.glob(os.path.join(folder_path, "*.csv"))
    if not csv_files:
        print(f"No CSV files found in folder '{folder_path}'.")
        return

    dataframes = []

    for file in csv_files:
        try:
            # Read CSV while treating 'N/A' as a regular string
            df = pd.read_csv(file, keep_default_na=False, encoding='utf-8')
            df.columns = df.columns.str.strip()  # Remove extra spaces from column names
            dataframes.append(df)
            print(f"File '{file}' processed successfully.")
        except Exception as e:
            print(f"Error reading file '{file}': {e}")

    if not dataframes:
        print("No valid data to process.")
        return

    # Combine all DataFrames
    combined_df = pd.concat(dataframes, ignore_index=True)

    try:
        combined_df.to_csv(output_file, index=False, na_rep="", encoding='utf-8')
        print(f"All files have been combined into '{output_file}' successfully!")
    except Exception as e:
        print(f"Error writing combined file: {e}")
        return

    # Cleanup: Remove the folder
    cleanup_folder(folder_path)

def cleanup_folder(folder_path):
    try:
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)
            print(f"Folder '{folder_path}' has been removed successfully!")
    except Exception as e:
        print(f"Error removing folder '{folder_path}': {e}")

