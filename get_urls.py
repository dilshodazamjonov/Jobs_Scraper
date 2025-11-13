import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import random
from clean_andCheck_last_date import clean_and_check_date

class Extract_urls:
    def __init__(self, driver, wait, ec):
        self.driver = driver
        self.wait = wait
        self.ec = ec

    urls = []

    def load_data(self):
        page_num = 1  # Start from page 1
        while True:
            try:
                # Find job titles on the current page
                job_titles = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'item_recruit')]//div[@class='area_job']//h2[@class='job_tit']/a")
                
                dates = self.driver.find_elements(By.XPATH, "//*[@class='job_day']")
                # Find and print the number of job listings on the current page
                print(f"Page {page_num}: Found {len(job_titles)} job listings")
                
                check = True
                # Extract job URLs
                job_urls = [url.get_attribute("href") for url in job_titles]
                print(f"Total job URLs found on page {page_num}: {len(job_urls)}")
                for job_url,date in zip(job_urls, dates):
                    check = clean_and_check_date(date.text)
                    if check == False:
                        break
                    self.urls.append(job_url)

                if check == False:
                    break
                # Try to click the "Next Page" button or link
                pagination_link = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, f"//a[@page='{page_num + 1}']"))
                )
                print(f"Navigating to page {page_num + 1}")
                pagination_link.click()
                page_num += 1

                # Sleep between page navigations to simulate human behavior
                time.sleep(random.uniform(3, 6)) 

            except Exception as e:
                # If an error occurs (such as no next page), break the loop
                print(f"Error: {e}. Exiting pagination loop.")
                break

    def get_urls(self):
        return self.urls
