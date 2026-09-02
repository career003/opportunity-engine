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
Generate up to 6 real, highly valuable career opportunities, internships, jobs, or scholarships based on current market trends for students and young professionals in India and globally.

CRITICAL REQUIREMENT FOR LINKS: Do not use AI development platforms, Google Studio, or raw code repository links. For each item, provide a direct official career portal or application URL (e.g., https://www.ncs.gov.in, https://scholarships.gov.in, https://careers.google.com, or official organizational career pages).

Return ONLY a valid JSON array with objects containing these exact keys: 
"category" (choose strictly from: TODAY'S JOBS, SCHOLARSHIPS, REMOTE JOBS, INTERNSHIPS, FREE COURSES, COMPETITIONS, AI TOOLS), 
"title", "organization", "location", "eligibility", "deadline", "salary", "qualification", "description", "source_url".
No markdown formatting blocks around it, just raw JSON.
"""

response = model.generate_content(prompt)
clean_text = response.text.replace("```json", "").replace("```", "").strip()

try:
    new_data = json.loads(clean_text)
    # Ensure source_url field maps correctly for frontend consumption and filters out unwanted domains
    for item in new_data:
        url = item.get("source_url", "")
        if not url.startswith("http") or "aistudio.google.com" in url or "github.com" in url:
            item["source_url"] = "https://www.ncs.gov.in"

    with open("opportunities.json", "w") as f:
        json.dump(new_data, f, indent=4)
        
except Exception as e:
    print(f"Error parsing AI output: {e}")
