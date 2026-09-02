import json
import os
import urllib.request
import xml.etree.ElementTree as ET
import google.generativeai as genai

# Configure Gemini API
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-3.6-flash")

# Fetch real raw text from a public education/career RSS feed
rss_url = "https://news.google.com/rss/search?q=internships+jobs+students+India&hl=en-IN&gl=IN&ceid=IN:en"

try:
    req = urllib.request.Request(rss_url, headers={'User-Agent': 'Mozilla/5.0'})
    feed_data = urllib.request.urlopen(req).read()
    root = ET.fromstring(feed_data)
    
    raw_items = []
    for item in root.findall('.//item')[:10]:
        title = item.find('text').text if item.find('text') is not None else item.find('title').text
        link = item.find('link').text
        raw_items.append(f"Title: {title} | Link: {link}")
    
    raw_text_corpus = "\n".join(raw_items)
except Exception as e:
    raw_text_corpus = "Tech internships in India, National Scholarship Portal updates."

# Prompt Gemini to process the real data into your website's format
prompt = f"""
Analyze the following raw feed items and extract up to 3 real, valid career opportunities, internships, jobs, or scholarships for students/job seekers in India.
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
    
    # Load existing data if available
    if os.path.exists("opportunities.json"):
        with open("opportunities.json", "r") as f:
            existing_data = json.load(f)
    else:
        existing_data = []

    # Combine and save top entries
    combined_data = new_data + existing_data
    with open("opportunities.json", "w") as f:
        json.dump(combined_data[:30], f, indent=4)
        
except Exception as e:
    print(f"Error parsing AI output: {e}")
