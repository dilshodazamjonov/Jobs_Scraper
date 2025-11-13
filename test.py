import time
from random import randint
from datetime import datetime

import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


def translate_to_english(text):
    # Dummy translator for testing
    return text


def clean_and_format_first_date(raw_date):
    """
    Fake cleaner for now — just returns today's date in MM/DD/YYYY format.
    """
    return datetime.now().strftime("%m/%d/%Y")


def extract_skills(text_blocks):
    """
    Dummy skill extractor for test.
    """
    return "None found"


class Extract:
    VALID_TITLES = [
        "Backend developer", "Frontend developer", "Data analyst", "Data engineer", "Data scientist",
        "AI engineer", "Android developer", "IOS developer", "Game developer", "DevOps engineer",
        "IT project manager", "Network engineer", "Cybersecurity Analyst", "Cloud Architect", "Full stack developer"
    ]

    def __init__(self):
        self.data = []

    def data_scrapping(self, list_of_urls: list):
        if not list_of_urls:
            print("No URLs provided.")
            return

        options = webdriver.ChromeOptions()
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--start-maximized")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        wait = WebDriverWait(driver, 15)

        for url in list_of_urls:
            try:
                driver.get(url)
                time.sleep(randint(2, 5))
                job = self._extract_data_from_driver(driver, wait, EC)
                self.data.append(job)
            except Exception as e:
                print(f"Error scraping {url}: {e}")

        driver.quit()

        df = pd.DataFrame(self.data)
        print(df)

    def _extract_data_from_driver(self, driver, wait, ec):
        def get_text_or_na(xpath):
            try:
                element = wait.until(ec.presence_of_element_located((By.XPATH, xpath)))
                txt = element.text.strip()
                if not txt:
                    return "N/A"
                return translate_to_english(txt)
            except Exception:
                return "N/A"

        company = get_text_or_na("//a[contains(@class, 'company')]")
        job_title = get_text_or_na("//h1[contains(@class, 'tit_job')]")
        location = get_text_or_na("//dl[dt[contains(text(),'근무지역')]]/dd")

        # Date cleanup
        raw_posted = get_text_or_na("//dl[dt[contains(text(),'시작일')]]/dd")
        try:
            posted_date = clean_and_format_first_date(raw_posted)
        except Exception:
            posted_date = datetime.now().strftime("%m/%d/%Y")

        salary = get_text_or_na("//dl[dt[contains(text(),'급여')]]/dd")

        # --- Job title classification ---
        lower_title = job_title.lower()
        job_from_list = "unknown"
        for valid in self.VALID_TITLES:
            key = valid.lower().split()[0]
            if key in lower_title:
                job_from_list = valid
                break

        # --- Skills ---
        skills = "None found"
        try:
            target = wait.until(ec.presence_of_element_located((By.XPATH, '//*[@id="content"]/div[3]/section[1]')))
            text_blocks = [t.text.strip() for t in target.find_elements(By.XPATH, "./*") if t.text.strip()]
            full_text = " ".join(text_blocks)
            skills = extract_skills([full_text])
        except Exception:
            pass

        return {
            "ID": len(self.data) + 1,
            "Posted_date": posted_date,
            "Job Title from List": job_from_list,
            "Job Title": job_title,
            "Company": company,
            "Company Logo URL": "N/A",
            "Country": "South Korea",
            "Location": location,
            "Skills": skills,
            "Salary Info": salary,
            "Source": "saramin.co",
        }


if __name__ == "__main__":
    url = "https://www.saramin.co.kr/zf_user/jobs/relay/view?isMypage=no&rec_idx=52060402&recommend_ids=eJxVj7kRw0AMA6txDuD4xi5E%2FXfhG3ksnkMMHi5dbDjtKvKVbxcRq3Q19JVNs3EFmTBhd8%2F1k6DCLMfNyuZ0V%2Fp6lhlYrJpw00N%2FGLt7YCRODFs9YYXMHgx273SMW0Afh4Q4puBZHGY5Yqb2g03dhz732z%2BZ&view_type=search&searchword=Data+engineer&searchType=search&gz=1&t_ref_content=generic&t_ref=search&relayNonce=399ff38177eae08f7ea3&paid_fl=n&search_uuid=76d4ccf1-2417-4350-b348-cf06a0315b9f&immediately_apply_layer_open=n#seq=0"
    extractor = Extract()
    extractor.data_scrapping([url])
