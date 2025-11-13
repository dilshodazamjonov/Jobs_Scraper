import google.generativeai as genai
from Title_tocsv import to_csv

key = "AIzaSyCJRs7UZZ4LCOzhGVQdR0U2Q0VR771bBjs"

genai.configure(api_key=key)  # Configure once globally

def identify_tite(titles: list, skills: list):
    """
    Map scraped job titles and skills to predefined job titles using Gemini API.
    """
    if len(titles) != len(skills):
        print("Titles and skills list must be the same length!")
        return

    # Prepare input for the AI
    prompt = f"""
You are an expert in job titles and IT job roles. You are given a list of job titles and corresponding skills.
Your task is to match each job title to the closest predefined job title below. Only return titles from this list:

- Backend developer
- Frontend developer
- Data analyst
- Data engineer
- Data scientist
- AI engineer
- Android developer
- IOS developer
- Game developer
- DevOps engineer
- IT project manager
- Network engineer
- Cybersecurity Analyst
- Cloud Architect
- Full stack developer

Rules:
1. Return only one title per input item.
2. If the input is vague or missing, use skills to determine the best match.
3. If no match can be found, return "unknown".
4. Output a **comma-separated list** matching the input order. The length must equal the number of input titles.

Input titles: {titles}
Input skills: {skills}
"""

    try:
        model = genai.GenerativeModel("models/gemini-2.5-flash-lite")
        response = model.generate_content(prompt)

        output_text = response.text.strip()
        output_list = [x.strip() for x in output_text.split(",")]

        # Safety: ensure the output length matches input
        if len(output_list) != len(titles):
            print("Warning: output length mismatch. Filling unknowns.")
            output_list = (output_list + ["unknown"] * len(titles))[:len(titles)]

        print("Mapped job titles:", output_list)
        to_csv(titles=output_list)

    except Exception as e:
        print("API Error:", e)


# # ----------------------------
# # TEST EXAMPLE
# # ----------------------------
# sample_titles = ["웹 개발자", "데이터 분석가", "인공지능 연구원"]
# sample_skills = ["Python, Django", "SQL, Excel, Python", "Machine Learning, Python, TensorFlow"]

# identify_tite(sample_titles, sample_skills)
