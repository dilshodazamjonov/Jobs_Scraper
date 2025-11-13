import pyodbc
import pandas as pd


def insert_data_to_sql(data_directory):
    """
    This function processes the CSV files from the provided directory, cleans and appends them into a DataFrame,
    then inserts the data into a specified SQL Server database.

    Parameters:
        data_directory (str): Path to the directory containing CSV files.
        server (str): SQL Server address.
        database (str): SQL Server database name.
        table_name (str): The name of the table to insert the data into.
    """
    try:
        # Assuming append_csv_files is defined elsewhere and returns a DataFrame
        final_dataframe = pd.read_csv("cleaned_job_titles.csv")
             # Replace missing or blank Salary values with "N/A"
        if 'Salary Info' in final_dataframe.columns:
            final_dataframe['Salary Info'] = final_dataframe['Salary Info'].fillna('N/A').replace('', 'N/A')

        if 'Company Logo URL' in final_dataframe.columns:
            final_dataframe['Company Logo URL'] = final_dataframe['Company Logo URL'].fillna('N/A').replace('', 'N/A')    

        # SQL Server connection setup
        conn = pyodbc.connect(
        'Driver={SQL Server};'
        'Server=POWERBI-1\IT_JOBS;'
        'Database=IT_JOBS;'
        'UID=sa;'                # SQL Server username
        'PWD=maab2024'          # SQL Server password
    )

        cursor = conn.cursor()

        # Create the table if it doesn't exist
        create_table_query = f"""
                IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'JobListings')
                BEGIN
                    CREATE TABLE JobListings (
                        ID INT,
                        Posted_date NVARCHAR(100),
                        Job_Title_from_List NVARCHAR(255),
                        Job_Title NVARCHAR(255),
                        Company NVARCHAR(255),
                        Company_Logo_URL NVARCHAR(MAX),
                        Country NVARCHAR(50),
                        Location NVARCHAR(255),
                        Skills NVARCHAR(MAX),
                        Salary_Info NVARCHAR(255),
                        Source NVARCHAR(255)
                    )
                END
                """
        cursor.execute(create_table_query)
        conn.commit()

        # Insert data into the table
        insert_query = f"""
                INSERT INTO JobListings (ID, Posted_date, Job_Title_from_List, Job_Title, Company, Company_Logo_URL, Country, Location, Skills, Salary_Info, Source)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """

        for _, job in final_dataframe.iterrows():
            try:
                cursor.execute(insert_query,
                               int(job['ID']),
                               job['Posted_date'],
                               job['Job Title from List'],
                               job['Job Title'],
                               job['Company'],
                               job['Company Logo URL'],
                               job['Country'],
                               job['Location'],
                               job['Skills'],
                               job['Salary Info'],
                               job['Source'])
            except Exception as row_error:
                print(f"Failed to insert row {_}: {row_error}")

        conn.commit()
        cursor.close()
        conn.close()
        print("Data saved to SQL Server")

    except Exception as e:
        print(f"Failed to save data to SQL Server: {e}")



# def insert_data_to_sql():
#     """
#     This function processes the CSV files from the provided directory, cleans and appends them into a DataFrame,
#     then inserts the data into a specified SQL Server database.

#     Parameters:
#         data_directory (str): Path to the directory containing CSV files.
#         server (str): SQL Server address.
#         database (str): SQL Server database name.
#         table_name (str): The name of the table to insert the data into.
#     """
#     try:
#         # Assuming append_csv_files is defined elsewhere and returns a DataFrame
#         final_dataframe = pd.read_csv("cleaned_job_titles.csv")
#              # Replace missing or blank Salary values with "N/A"
#         if 'Salary Info' in final_dataframe.columns:
#             final_dataframe['Salary Info'] = final_dataframe['Salary Info'].fillna('N/A').replace('', 'N/A')

#         if 'Company Logo URL' in final_dataframe.columns:
#             final_dataframe['Company Logo URL'] = final_dataframe['Company Logo URL'].fillna('N/A').replace('', 'N/A')    

#         conn = pyodbc.connect(
#             "DRIVER={ODBC Driver 17 for SQL Server};"
#             "SERVER=SARDOR;"
#             "DATABASE=IT_JOBS;"
#             "Trusted_Connection=yes;"
#         )

#         cursor = conn.cursor()

#         # Create the table if it doesn't exist
#         create_table_query = f"""
#                 IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'JobListings')
#                 BEGIN
#                     CREATE TABLE JobListings (
#                         ID INT,
#                         Posted_date NVARCHAR(100),
#                         Job_Title_from_List NVARCHAR(255),
#                         Job_Title NVARCHAR(255),
#                         Company NVARCHAR(255),
#                         Company_Logo_URL NVARCHAR(MAX),
#                         Country NVARCHAR(50),
#                         Location NVARCHAR(255),
#                         Skills NVARCHAR(MAX),
#                         Salary_Info NVARCHAR(255),
#                         Source NVARCHAR(255)
#                     )
#                 END
#                 """
#         cursor.execute(create_table_query)
#         conn.commit()

#         # Insert data into the table
#         insert_query = f"""
#                 INSERT INTO JobListings (ID, Posted_date, Job_Title_from_List, Job_Title, Company, Company_Logo_URL, Country, Location, Skills, Salary_Info, Source)
#                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
#                 """

#         for _, job in final_dataframe.iterrows():
#             try:
#                 cursor.execute(insert_query,
#                                int(job['ID']),
#                                job['Posted_date'],
#                                job['Job Title from List'],
#                                job['Job Title'],
#                                job['Company'],
#                                job['Company Logo URL'],
#                                job['Country'],
#                                job['Location'],
#                                job['Skills'],
#                                job['Salary Info'],
#                                job['Source'])
#             except Exception as row_error:
#                 print(f"Failed to insert row {_}: {row_error}")

#         conn.commit()
#         cursor.close()
#         conn.close()
#         print("Data saved to SQL Server")

#     except Exception as e:
#         print(f"Failed to save data to SQL Server: {e}")

# insert_data_to_sql()