import time
from random import randint
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from extractskill import extract_skills
from Translation import translate_to_english


def clean_and_format_first_date(text):
    # Simple placeholder cleaner
    return text.strip() if text else "N/A"


class Extract:
    def __init__(self):
        pass

    def data_scrapping(self, list_of_urls: list):
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
                time.sleep(randint(2, 4))
                self.__extract_data(driver, wait, EC)
            except Exception as e:
                print(f"Error processing {url}: {e}")
                continue

        driver.quit()

    def __extract_data(self, driver, wait, ec):
        # Company
        company_xpath = "//a[contains(@class, 'company')]"
        company = self.__get_text_or_nan(By.XPATH, company_xpath, wait, ec, driver)
        company = translate_to_english(company)
        print(f"Company: {company}")

        # Job title
        job_title_xpath = "//h1[contains(@class, 'tit_job')]"
        job_title = self.__get_text_or_nan(By.XPATH, job_title_xpath, wait, ec, driver)
        job_title = translate_to_english(job_title)
        print(f"Job Title: {job_title}")

        # Location
        location_xpath = "//dl[dt[contains(text(),'근무지역')]]/dd"
        location = self.__get_text_or_nan(By.XPATH, location_xpath, wait, ec, driver)
        location = translate_to_english(location)
        print(f"Location: {location}")

        # Posted Date
        posted_date_xpath = "//dl[dt[contains(text(),'시작일')]]/dd"
        posted_date = self.__get_text_or_nan(By.XPATH, posted_date_xpath, wait, ec, driver)
        posted_date = clean_and_format_first_date(posted_date)
        print(f"Posted Date: {posted_date}")

        # ✅ Salary
        salary_xpath = "//dl[dt[contains(text(),'급여')]]/dd"
        salary = self.__get_text_or_nan(By.XPATH, salary_xpath, wait, ec, driver)
        salary = translate_to_english(salary)
        print(f"Salary: {salary}")

        # Skills (after extraction → cleanup)
        skills = self.__get_skills_from_page(wait, ec)
        if isinstance(skills, list):
            skills_str = ", ".join(skills)
        else:
            skills_str = skills if skills and skills.strip() else "None found"
        skills_str = skills_str.replace(",", ", ").replace("  ", " ").strip()
        print(f"Skills: {skills_str}")

    def __get_text_or_nan(self, locator_type, locator_value, wait, ec, driver):
        try:
            element = wait.until(ec.presence_of_element_located((locator_type, locator_value)))
            return element.text.strip() if element and element.text.strip() else "N/A"
        except Exception:
            return "N/A"

    def __get_skills_from_page(self, wait, ec):
        texts = []
        try:
            target_element = wait.until(
                ec.presence_of_element_located((By.XPATH, '//*[@id="content"]/div[3]/section[1]'))
            )
            for child in target_element.find_elements(By.XPATH, './*'):
                # Try to find stopping element
                try:
                    stop = child.find_element(By.XPATH, '//*[@id="content"]/div[3]/section[2]/div/div[7]/div[1]/h2/font/font')
                except Exception:
                    try:
                        stop = child.find_element(By.XPATH, '//*[@id="content"]/div[3]/section[2]/div/div[9]/div[1]/h2/font/font')
                    except Exception:
                        stop = None

                text = translate_to_english(child.text.strip())
                if stop:
                    break
                texts.append(text)

            # ✅ Only clean & join *after* extraction worked
            full_text = " ".join(texts)
            if not full_text.strip():
                return " "
            result = extract_skills([full_text])
            # If extract_skills returns garbage characters like C, S, S — clean up
            if isinstance(result, list):
                result = [r.strip() for r in result if len(r.strip()) > 1]
            return result if result else " "

        except Exception:
            return " "


if __name__ == "__main__":
    urls = [
        "https://www.saramin.co.kr/zf_user/jobs/relay/view?isMypage=no&rec_idx=52291534&recommend_ids=eJxNjrsRA1EIA6txDuInYhdy%2FXfhd%2FacIdxZhBTQllC%2FqHzVO4B0Vl0tuPFIpsex9cMwMy5UC38QKqW1sNV9Ph%2BMxN8CLaKD7DJ%2Feu8ZlToocKkZSbatLKTbpkjJyrFJi2WdqXtVINcxmZgiIRzf7AdY6UBC&view_type=search&searchType=search&gz=1&t_ref_content=generic&t_ref=search&relayNonce=e62c94e11d50abc8201d&paid_fl=n&search_uuid=91e25297-6508-40a9-b3f8-0583bab5d91c&immediately_apply_layer_open=n#seq=2"
    ]

    scraper = Extract()
    scraper.data_scrapping(urls)
