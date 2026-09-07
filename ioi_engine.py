import google.generativeai as genai
import fitz  # PyMuPDF
import json

class IOIAgent:
    def __init__(self, api_key):
        genai.configure(api_key=api_key)
        # Using Gemini 1.5 Pro with native Google Search grounding
        self.model = genai.GenerativeModel(
            model_name='gemini-1.5-pro',
            tools=[{"google_search_retrieval": {}}]
        )

    def parse_cv(self, pdf_file):
        """Extracts and structures CV data."""
        doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
        text = " ".join([page.get_text() for page in doc])
        
        prompt = f"""
        Extract the following into a JSON object: 
        Full Name, University, Degree, Grad Year, Skills (Technical & Soft), 
        Previous Internships, and 3 key 'Selling Points'.
        CV Content: {text}
        """
        response = self.model.generate_content(prompt)
        return response.text

    def search_high_signal_leads(self, industry, location, profile):
        """Discovers companies using real-time Google Search grounding."""
        prompt = f"""
        Act as a Finance & Consulting Headhunter.
        Search for {industry} firms in {location}.
        Identify 5 specific firms that have RECENT 'Opportunity Signals' (fundraising, new office, acquisitions).
        Candidate Profile Context: {profile}

        Return a JSON list of objects with: company, signal, contact, score (0-100), why.
        """
        response = self.model.generate_content(prompt)
        return response.text

    def generate_outreach(self, lead, profile):
        """Generates personalized outreach."""
        prompt = f"""
        Write a concise LinkedIn connection request (max 300 chars) for:
        Target: {lead}
        Candidate Background: {profile}
        - Refer specifically to their recent activity.
        - Brief and professional.
        """
        response = self.model.generate_content(prompt)
        return response.text
