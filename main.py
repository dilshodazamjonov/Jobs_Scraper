from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import time
from threadis import assign_lists_to_threads
from get_urls import Extract_urls
from Scrapping import Extract
from collect_all_csv import collect_csv
from File_ti_list_to_ai import give_to_ai
from cleaned_and_identified_data import cleaned_data_to_csv

from push_to_database import insert_data_to_sql # type: ignore
# Set up Chrome option
options = webdriver.ChromeOptions()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--start-maximized")

# Set up WebDriver
cService = Service(executable_path=r"C:\Program Files (x86)\chromedriver-win64\chromedriver-win64\chromedriver.exe")
driver = webdriver.Chrome(service=cService, options=options)

driver.get("https://www.saramin.co.kr/zf_user/search?cat_mcls=2&company_cd=0%2C1%2C2%2C3%2C4%2C5%2C6%2C7%2C9%2C10&cat_kewd=1658&panel_type=&search_optional_item=y&search_done=y&panel_count=y&preview=y&recruitPage=1&recruitSort=reg_dt&recruitPageCount=40&inner_com_type=&searchword=&show_applied=&quick_apply=&except_read=&ai_head_hunting=&mainSearch=n")
time.sleep(5)

wait = WebDriverWait(driver, 10)

# --- Step 1: Extract URLs ---
url_extractor = Extract_urls(driver=driver, wait=wait, ec=EC)
url_extractor.load_data()
lst = url_extractor.get_urls()
driver.quit()

# --- Step 2: Scrape job details using threads ---
data = Extract(final_file="cleaned_job_titles.csv")
threads = assign_lists_to_threads(data, lst[:11])
for t in threads:
    t.join()

# --- Step 2: Save final scraped data ---
data.save_to_csv()  # everything is in one CSV

# --- Step 3: Run AI mapping on final CSV ---
give_to_ai("cleaned_job_titles.csv")

# --- Step 4: Clean unknown titles and finalize ---
cleaned_data_to_csv(final_file="cleaned_job_titles.csv")  # merge AI titles into the same CSV


# --- Step 6: Push to database ---
# insert_data_to_sql()
