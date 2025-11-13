import pandas as pd
from title_identify_with_ai import identify_tite

def give_to_ai(input_file="cleaned_job_titles.csv"):
    """
    Reads the final scraped CSV and sends Job Title + Skills to AI for mapping.
    Saves results back to Title.csv (or similar) for merging later.
    """
    try:
        df = pd.read_csv(input_file)
    except FileNotFoundError:
        print(f"File '{input_file}' not found. Skipping AI processing.")
        return

    titles = df["Job Title"].tolist()
    skills = df["Skills"].tolist()

    batch_size = 10
    for i in range(0, len(titles), batch_size):
        titles_batch = titles[i:i + batch_size]
        skills_batch = skills[i:i + batch_size]
        identify_tite(titles=titles_batch, skills=skills_batch)
