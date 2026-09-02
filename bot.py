import json
import os
import urllib.request
import xml.etree.ElementTree as ET
import google.generativeai as genai

genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-3.6-flash")

rss_url = "https://news.google.com/rss/search?q=internships+jobs+students+scholarships+India&hl=en-IN&gl=IN&ceid=IN:en"

try:
    req = urllib.request.Request(rss_url, headers={'User-Agent': 'Mozilla/5.0'})
    feed_data = urllib.request.urlopen(req).read()
    root = ET.fromstring(feed_data)
    
    raw_items = []
    for item in root.findall('.//item')[:10]:
        title = item.find('title').text if item.find('title') is not None else "Opportunity"
        raw_items.append(f"Title: {title}")
    
    raw_text_corpus = "\n".join(raw_items)
except Exception as e:
    raw_text_corpus = "Tech internships in India, National Scholarship Portal updates, government jobs."

prompt = f"""
Generate up to 6 real career opportunities, internships, jobs, or scholarships for students and young professionals.

CRITICAL REQUIREMENT FOR LINKS ("source_url"): 
- Every single item MUST contain a working external URL (e.g., https://www.linkedin.com/jobs, https://www.naukri.com, or specific company career sites).
- Do NOT use placeholder text, relative paths, localhost, GitHub repo links, or AI studio links.

Return ONLY a valid JSON array with objects containing these exact keys: 
"category" (choose strictly from: TODAY'S JOBS, SCHOLARSHIPS, REMOTE JOBS, INTERNSHIPS, FREE COURSES, COMPETITIONS, AI TOOLS), 
"title", "organization", "location", "eligibility", "deadline", "salary", "qualification", "description", "source_url".
No markdown formatting blocks around it, just raw JSON.
"""

response = model.generate_content(prompt)
clean_text = response.text.replace("```json", "").replace("```", "").strip()

try:
    new_data = json.loads(clean_text)
    
    # Force clean valid links for every card type
    for item in new_data:
        url = item.get("source_url", "")
        category = item.get("category", "")
        
        if not url.startswith("http") or any(bad in url for bad in ["aistudio.google.com", "github.com", "localhost", "127.0.0.1"]):
            if category == "INTERNSHIPS":
                item["source_url"] = "https://www.naukri.com/internships"
            elif category == "REMOTE JOBS":
                item["source_url"] = "https://www.linkedin.com/jobs/search/?f_WT=2"
            else:
                item["source_url"] = "https://www.naukri.com"

    with open("opportunities.json", "w") as f:
        json.dump(new_data, f, indent=4)
        
except Exception as e:
    print(f"Error parsing AI output: {e}")
