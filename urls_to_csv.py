import pandas as pd
def write_to_csv(all_urls : list):
    data = {
        "Urls" : all_urls
    }

    df = pd.DataFrame(data)
    df.to_csv("urls.csv", mode="w", index=False)
