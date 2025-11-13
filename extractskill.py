from job_skills_mapping import tools_list

import re

def extract_skills(texts, skills_list=tools_list):
    full_text = " ".join(texts).lower()
    extracted_skills = [
        skill for skill in skills_list
        if re.search(rf'(\b|#){re.escape(skill.lower())}(\b|#)', full_text)
    ]
    if not extracted_skills:
        return " "
    skills_text = ", ".join(sorted(set(extracted_skills)))
    return skills_text

