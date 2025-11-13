import threading
import time
from random import randint
from datetime import datetime
import os

import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from extractskill import extract_skills
from Translation import translate_to_english
from Data_time_clean import clean_and_format_first_date


class Extract:
    """
    Thread-safe scraper. Each thread calls data_scrapping(list_of_urls).
    Threads append results to the shared self._data list under a lock.
    After all threads finish, call save_to_csv() exactly once.
    """

    VALID_TITLES = [
        "Backend developer", "Frontend developer", "Data analyst", "Data engineer", "Data scientist",
        "AI engineer", "Android developer", "IOS developer", "Game developer", "DevOps engineer",
        "IT project manager", "Network engineer", "Cybersecurity Analyst", "Cloud Architect", "Full stack developer"
    ]

    def __init__(self, final_file="cleaned_job_titles.csv", overwrite=True, checkpoint_every=0):
        self.final_file = final_file
        self.overwrite = overwrite
        self.checkpoint_every = int(checkpoint_every or 0)

        # In-memory storage and synchronization
        self._data = []
        self._lock = threading.Lock()
        self._next_id = 1

        # If overwrite requested, remove existing file at start (optional)
        if self.overwrite and os.path.exists(self.final_file):
            try:
                os.remove(self.final_file)
            except Exception:
                pass

    # -------------------------
    # Public: thread target
    # -------------------------
    def data_scrapping(self, list_of_urls: list):
        """
        This is intended to be called by a thread. Each thread creates its own webdriver,
        scrapes its sublist, and appends results to the shared storage under a lock.
        This function DOES NOT save CSV files (to avoid race conditions).
        """
        if not list_of_urls:
            return

        options = webdriver.ChromeOptions()
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--start-maximized")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        wait = WebDriverWait(driver, 15)

        try:
            for url in list_of_urls:
                try:
                    driver.get(url)
                    time.sleep(randint(2, 5))
                    job = self._extract_data_from_driver(driver, wait, EC)

                    # append job to shared list with lock and assign ID
                    with self._lock:
                        job["ID"] = self._next_id
                        self._next_id += 1
                        self._data.append(job)

                        # optional checkpoint write
                        if self.checkpoint_every > 0 and (len(self._data) % self.checkpoint_every) == 0:
                            self._checkpoint_save()

                except Exception as e:
                    # do not crash the whole thread on single-URL error
                    print(f"Error processing {url}: {e}")
                    continue

        except KeyboardInterrupt:
            print("\nScraping stopped by user (KeyboardInterrupt).")
        finally:
            try:
                driver.quit()
            except Exception:
                pass
        # thread finishes, but does not save file

    # -------------------------
    # Internal helpers
    # -------------------------
    def _extract_data_from_driver(self, driver, wait, ec):
        """Extract raw job fields from an already-loaded page. Returns a dict (without ID)."""

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

        # Posted date - use clean_and_format_first_date if possible, else today's date
        raw_posted = get_text_or_na("//dl[dt[contains(text(),'시작일')]]/dd")
        try:
            posted_date = clean_and_format_first_date(raw_posted) or None
        except Exception:
            posted_date = None

        if not posted_date:
            # fallback to today's date in same format MM/DD/YYYY
            posted_date = datetime.now().strftime("%m/%d/%Y")

        salary = get_text_or_na("//dl[dt[contains(text(),'급여')]]/dd")

        # Skills: build a full_text from content section then extract
        skills = self._get_skills_from_driver(driver, wait, ec)
        # normalize skills to consistent string
        if isinstance(skills, list):
            skills_str = ", ".join([s.strip() for s in skills if s.strip()])
        else:
            skills_str = str(skills).strip()
        skills_str = skills_str if skills_str and skills_str != " " else "None found"

        # Guess job title from title + skills (so Job Title from List is useful immediately)
        guessed_title = self._guess_job_title(job_title, skills_str)

        # final job dict (ID assigned by caller under lock)
        job_data = {
            "ID": None,
            "Posted_date": posted_date,
            "Job Title from List": guessed_title,
            "Job Title": job_title,
            "Company": company,
            "Company Logo URL": "N/A",
            "Country": "South Korea",
            "Location": location,
            "Skills": skills_str,
            "Salary Info": salary,
            "Source": "saramin.co",
        }
        return job_data

    def _get_skills_from_driver(self, driver, wait, ec):
        """
        Extracts textual blocks from the content area, joins them and runs extract_skills.
        Returns a string (comma-separated) or 'None found'.
        """
        try:
            target_element = wait.until(ec.presence_of_element_located((By.XPATH, '//*[@id="content"]/div[3]/section[1]')))
            texts = []
            for child in target_element.find_elements(By.XPATH, "./*"):
                t = child.text.strip()
                if t:
                    texts.append(translate_to_english(t))
            full_text = " ".join(texts).strip()
            if not full_text:
                return "None found"

            # extract_skills returns a string (or " ") per your module; ensure we normalize
            result = extract_skills([full_text])
            if isinstance(result, list):
                # defensive: join if list
                result = ", ".join(result)
            # normalize odd returns like single space
            if not result or not str(result).strip():
                return "None found"
            # ensure consistent spacing and comma format
            return ", ".join([s.strip() for s in str(result).split(",") if s.strip()])
        except Exception:
            return "None found"

    def _guess_job_title(self, job_title: str, skills: str) -> str:
        """
        Lightweight heuristic classifier to map raw job title + skills to one of VALID_TITLES.
        Returns a string from VALID_TITLES or "unknown".
        """
        if not job_title:
            job_title = ""
        combined = f"{job_title} {skills}".lower()

        checks = [
            ("frontend", {"frontend", "front-end", "react", "vue", "angular", "javascript", "typescript", "css", "html", "next.js", "nextjs", "vite", "react query"}),
            ("backend", {"backend", "back-end", "node.js", "node", "django", "flask", "spring", "express", "java", "golang", "go", "php", "ruby", "sql", "postgresql", "mysql", "nestjs"}),
            ("fullstack", {"fullstack", "full-stack", "full stack", "full stack developer"}),
            ("data_scientist", {"data scientist", "ml", "machine learning", "deep learning", "pytorch", "tensorflow", "scikit-learn"}),
            ("data_engineer", {"data engineer", "etl", "airflow", "spark", "kafka", "databricks", "hadoop"}),
            ("data_analyst", {"data analyst", "excel", "tableau", "power bi", "qlik", "looker", "sql", "pandas"}),
            ("ai_engineer", {"ai", "llm", "gpt", "fine tune", "prompt", "transformer", "mlops", "mlo ps", "model", "llama", "hf", "hugging face"}),
            ("android", {"android", "kotlin", "java (android)", "android sdk"}),
            ("ios", {"ios", "swift", "objective-c", "xcode"}),
            ("game", {"unity", "unreal", "game", "gameplay", "cocos"}),
            ("devops", {"devops", "kubernetes", "docker", "ci/cd", "jenkins", "terraform", "ansible"}),
            ("itpm", {"project manager", "pm", "it project manager", "project management"}),
            ("network", {"network", "network engineer", "routing", "switch", "cisco", "firewall", "palo alto"}),
            ("security", {"security", "information security", "infosec", "cybersecurity", "vulnerability", "pentest", "owasp"}),
            ("cloud", {"cloud", "aws", "azure", "gcp", "cloud architect", "cloud engineer", "fargate", "lambda", "ecs", "ecr"})
        ]

        # Check in order and return first match mapped to VALID_TITLES
        for key, keywords in checks:
            if any(k in combined for k in keywords):
                if key == "frontend":
                    return "Frontend developer"
                if key == "backend":
                    return "Backend developer"
                if key == "fullstack":
                    return "Full stack developer"
                if key == "data_scientist":
                    return "Data scientist"
                if key == "data_engineer":
                    return "Data engineer"
                if key == "data_analyst":
                    return "Data analyst"
                if key == "ai_engineer":
                    return "AI engineer"
                if key == "android":
                    return "Android developer"
                if key == "ios":
                    return "IOS developer"
                if key == "game":
                    return "Game developer"
                if key == "devops":
                    return "DevOps engineer"
                if key == "itpm":
                    return "IT project manager"
                if key == "network":
                    return "Network engineer"
                if key == "security":
                    return "Cybersecurity Analyst"
                if key == "cloud":
                    return "Cloud Architect"

        # fallback: look for 'front'/'back' words explicitly
        if "front" in combined and any(w in combined for w in ["developer", "dev", "engineer", "frontend", "front-end"]):
            return "Frontend developer"
        if "back" in combined and any(w in combined for w in ["developer", "dev", "engineer", "backend", "back-end"]):
            return "Backend developer"

        return "unknown"

    # -------------------------
    # Saving / checkpointing
    # -------------------------
    def save_to_csv(self):
        """
        Save all accumulated data to final_file. Caller should call this once after all threads finish.
        If overwrite=True, file will be replaced. If overwrite=False and file exists, it will be appended.
        """
        with self._lock:
            if not self._data:
                print("No data to save.")
                return

            df = pd.DataFrame(self._data)

            # standardize columns & fill missing
            columns = ["ID", "Posted_date", "Job Title from List", "Job Title", "Company",
                       "Company Logo URL", "Country", "Location", "Skills", "Salary Info", "Source"]
            for col in columns:
                if col not in df.columns:
                    df[col] = "N/A"

            # save according to overwrite flag
            try:
                if self.overwrite or not os.path.exists(self.final_file):
                    df.to_csv(self.final_file, index=False, columns=columns)
                else:
                    # append without header
                    df.to_csv(self.final_file, mode="a", header=False, index=False, columns=columns)
                print(f"Saved {len(df)} jobs to '{self.final_file}'.")
            except Exception as e:
                print(f"Error saving CSV: {e}")

    def _checkpoint_save(self):
        """
        Save a checkpoint file named "<final_file>.checkpoint.csv".
        Called only under lock.
        """
        if not self._data:
            return
        try:
            checkpoint_file = f"{self.final_file}.checkpoint.csv"
            df = pd.DataFrame(self._data)
            columns = ["ID", "Posted_date", "Job Title from List", "Job Title", "Company",
                       "Company Logo URL", "Country", "Location", "Skills", "Salary Info", "Source"]
            for col in columns:
                if col not in df.columns:
                    df[col] = "N/A"
            df.to_csv(checkpoint_file, index=False, columns=columns)
            print(f"[checkpoint] Saved {len(df)} rows to '{checkpoint_file}'")
        except Exception as e:
            print(f"[checkpoint] Error saving checkpoint: {e}")
