import google.generativeai as genai
import fitz  # PyMuPDF
import json

class IOIAgent:
    def __init__(self, api_key):
        genai.configure(api_key=api_key)
        # Using Gemini 1.5 Pro with native Google Search grounding
        self.model = genai.GenerativeModel(
            model_name='gemini-1.5-pro',
            tools=[{"google_search_indexing": {}}]
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
        # Clean the response to ensure valid JSON
        return response.text

    def search_high_signal_leads(self, industry, location, profile):
        """Discovers companies using real-time Google Search grounding."""
        prompt = f"""
        Act as a Finance & Consulting Headhunter.
        Search for {industry} firms in {location}.
        Identify 5 specific firms that have RECENT 'Opportunity Signals':
        1. New fund launches or fundraising rounds.
        2. New office openings or leadership hires.
        3. Significant recent transactions/deals.
        
        For each firm, identify a likely professional contact (e.g., Partner, Principal, or Strategy Lead).
        
        Candidate Profile Context: {profile}

        Return a JSON list of objects:
        [
          {{
            "company": "Name",
            "signal": "Description of news",
            "contact": "Title/Level",
            "score": 0-100,
            "why": "Explanation of fit"
          }}
        ]
        """
        response = self.model.generate_content(prompt)
        return response.text

    def generate_outreach(self, lead, profile):
        """Generates hyper-personalized, non-generic outreach."""
        prompt = f"""
        Write a concise LinkedIn connection request (max 300 chars) and a short cold email.
        Target: {lead['contact']} at {lead['company']}
        The Hook: {lead['signal']}
        Candidate Background: {profile}
        
        Guidelines:
        - No 'I hope this finds you well'.
        - No 'highly motivated'.
        - Refer specifically to the company's recent activity ({lead['signal']}).
        - Professional, brief, and curiosity-driven.
        """
        response = self.model.generate_content(prompt)
        return response.text