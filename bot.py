import json
import os
import google.generativeai as genai

# Configure Gemini API
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-2.5-flash")

prompt = """
Generate 3 fresh, realistic career opportunities for students or job seekers in India today. 
Include a mix of 'TODAY'S JOBS', 'INTERNSHIPS', 'SCHOLARSHIPS', or 'FREE COURSES'.
Return ONLY a valid JSON array with objects containing these exact keys: 
"category", "title", "description", "link". No markdown formatting blocks around it, just raw JSON.
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

    # Prepend new entries so latest show up first
    combined_data = new_data + existing_data

    # Save back to file
    with open("opportunities.json", "w") as f:
        json.dump(combined_data[:30], f, indent=4) # Keep top 30 items max
        
except Exception as e:
    print(f"Error parsing AI output: {e}")
