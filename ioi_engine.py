import google.generativeai as genai
import fitz  # PyMuPDF
import json

class IOIAgent:
    def __init__(self, api_key):
        try:
            # Key ko clean karna zaroori hai (agar quotes aa gaye hon toh)
            clean_key = api_key.strip().strip('"').strip("'")
            genai.configure(api_key=clean_key)
            
            # Hum 'gemini-1.5-flash' use karenge kyunki ye fast aur stable hai
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            
            # Ek chhota sa test call check karne ke liye
            self.model.generate_content("test")
        except Exception as e:
            self.model = None
            print(f"Initialization Error: {e}")

    def parse_cv(self, pdf_file):
        """CV se skills aur experience extract karne ke liye"""
        if not self.model: return "Agent not initialized. Check API Key."
        try:
            doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
            text = " ".join([page.get_text() for page in doc])
            
            prompt = f"""
            Extract the following into a JSON-like summary: 
            Name, University, Degree, Key Skills, and Top 3 Selling Points.
            CV Text: {text[:8000]}
            """
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"CV Error: {str(e)}"

    def search_high_signal_leads(self, industry, location, profile):
        """Industry aur Location ke hisaab se internship targets dhundne ke liye"""
        if not self.model: return "API Key issues. Check Streamlit Secrets."
        
        prompt = f"""
        Act as a professional career coach and research analyst.
        Identify 5 real companies/firms in {location} for a {industry} internship.
        Focus on firms that are currently growing or active.
        For each, provide:
        - Company Name
        - Why it fits this candidate profile: {profile}
        - Recent news or 'Opportunity Signal' if possible.
        """
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Search Error: {str(e)}"

    def generate_outreach(self, lead, profile):
        """Personalized LinkedIn message banane ke liye"""
        if not self.model: return "Error"
        prompt = f"""
        Write a concise, professional LinkedIn connection request (max 300 characters).
        Target: {lead}
        Candidate Background: {profile}
        Rule: Direct, value-driven, no generic flattery.
        """
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except:
            return "Outreach generation failed."
