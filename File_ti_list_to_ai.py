import pandas as pd
from title_identify_with_ai import identify_tite
import time

# Read the CSV file
def give_to_ai():
    df = pd.read_csv("combined_output.csv")

    # Extract 'Job Title' and 'Skills' columns as lists
    titles = df["Job Title"].tolist()
    skills = df["Skills"].tolist()

    # Batch processing with specified batch size
    batch_size = 10
    for i in range(0, len(titles), batch_size):
        # Slice titles and skills for the current batch
        titles_batch = titles[i:i + batch_size]
        skills_batch = skills[i:i + batch_size]

        # Call the function with the current batch
        identify_tite(titles=titles_batch, skills=skills_batch)

        # Print the batch for debugging
        print(titles_batch)

        # Add a delay to avoid overwhelming the system
        time.sleep(5)
