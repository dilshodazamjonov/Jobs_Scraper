import pandas as pd
import os

def cleaned_data_to_csv():

    if not os.path.exists("Title.csv"):
        pd.DataFrame(columns=["Title"]).to_csv("Title.csv", index=False)

    # Read the combined data and titles
    df = pd.read_csv("combined_output.csv")
    df2 = pd.read_csv("Title.csv")

    # List of valid job titles
    valid_job_titles = [
        "Backend developer", "Frontend developer", "Data analyst", "Data engineer", "Data scientist", 
        "AI engineer", "Android developer", "IOS developer", "Game developer", "DevOps engineer", 
        "IT project manager", "Network engineer", "Cybersecurity Analyst", "Cloud Architect", "Full stack developer"
    ]

    # Map job titles from df2 to df
    df["Job Title from List"] = df2["Title"]

    # Step 1: Remove rows where the job title is "unknown"
    df_cleaned = df[df['Job Title from List'] != 'unknown']

    # Step 2: Remove rows where the job title is not in the valid job titles list
    df_cleaned = df_cleaned[df_cleaned['Job Title from List'].isin(valid_job_titles)]

    # Step 3: Set a fixed ID for each row
    df_cleaned["ID"] = range(1, len(df_cleaned) + 1)

        # Replace missing or blank Salary values with "N/A"
    if 'Salary Info' in df_cleaned.columns:
        df_cleaned['Salary Info'] = df_cleaned['Salary Info'].fillna('N/A').replace('', 'N/A')
        
    if 'Company Logo URL' in df_cleaned.columns:
        df_cleaned['Company Logo URL'] = df_cleaned['Company Logo URL'].fillna('N/A').replace('', 'N/A')    
    # Step 4: Save the cleaned data to a CSV file
    output_file = 'cleaned_job_titles.csv'
    df_cleaned.to_csv(output_file, index=False)

    print(f"Cleaned data saved to '{output_file}'")

    # Remove the used files
    for file in ["combined_output.csv", "Title.csv"]:
        if os.path.exists(file):
            os.remove(file)
            print(f"File '{file}' has been removed.")

