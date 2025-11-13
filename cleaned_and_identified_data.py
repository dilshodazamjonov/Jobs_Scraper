import pandas as pd
import os

def cleaned_data_to_csv(final_file="cleaned_job_titles.csv"):
    """
    Cleans scraped job data with AI-assigned titles in a single CSV.
    Updates 'Job Title from List' and removes invalid entries.
    """
    if not os.path.exists(final_file):
        print(f"Error: '{final_file}' not found. Cannot proceed.")
        return

    df = pd.read_csv(final_file)

    # Validate that AI-assigned titles exist
    if "Job Title from List" not in df.columns:
        df["Job Title from List"] = "unknown"

    # List of valid job titles
    valid_job_titles = [
        "Backend developer", "Frontend developer", "Data analyst", "Data engineer", "Data scientist",
        "AI engineer", "Android developer", "IOS developer", "Game developer", "DevOps engineer",
        "IT project manager", "Network engineer", "Cybersecurity Analyst", "Cloud Architect", "Full stack developer"
    ]

    # Remove unknown titles
    df_cleaned = df[df["Job Title from List"] != "unknown"]

    # Keep only valid job titles
    df_cleaned = df_cleaned[df_cleaned["Job Title from List"].isin(valid_job_titles)]

    if df_cleaned.empty:
        print("Warning: No valid job titles found after cleaning. CSV will not be saved.")
        return

    # Re-assign ID sequentially
    df_cleaned["ID"] = range(1, len(df_cleaned) + 1)

    # Fill missing values
    for col in ["Salary Info", "Company Logo URL"]:
        if col in df_cleaned.columns:
            df_cleaned[col] = df_cleaned[col].fillna("N/A").replace("", "N/A")

    # Save final cleaned CSV (overwrite the same file)
    df_cleaned.to_csv(final_file, index=False)
    print(f"Cleaned data saved to '{final_file}'")
