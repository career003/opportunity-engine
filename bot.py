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
    for item in root.findall('.//item')[:15]:
        title = item.find('title').text if item.find('title') is not None else "Opportunity"
        link = item.find('link').text if item.find('link') is not None else "#"
        raw_items.append(f"Title: {title} | Source Link: {link}")
    
    raw_text_corpus = "\n".join(raw_items)
except Exception as e:
    raw_text_corpus = "Tech internships in India, National Scholarship Portal updates, graduate jobs."

prompt = f"""
Analyze the following raw feed items and extract up to 6 real, valid career opportunities, internships, jobs, or scholarships for students/job seekers in India. 
For the "link" field, provide the direct official source link if present, or a clean valid URL. Do not use broken tracking links.

Raw Feed:
{raw_text_corpus}

Return ONLY a valid JSON array with objects containing these exact keys: 
"category" (choose from: TODAY'S JOBS, SCHOLARSHIPS, REMOTE JOBS, INTERNSHIPS, FREE COURSES, COMPETITIONS), 
"title", "description", "link". 
No markdown formatting blocks around it, just raw JSON.
"""

response = model.generate_content(prompt)
clean_text = response.text.replace("```json", "").replace("```", "").strip()

try:
    new_data = json.loads(clean_text)
    if os.path.exists("opportunities.json"):
        with open("opportunities.json", "r") as f:
            existing_data = json.load(f)
    else:
        existing_data = []

    combined_data = new_data + existing_data
    with open("opportunities.json", "w") as f:
        json.dump(combined_data[:30], f, indent=4)
        
except Exception as e:
    print(f"Error parsing AI output: {e}")
