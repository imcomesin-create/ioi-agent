import google.generativeai as genai
import fitz  # PyMuPDF
import json

class IOIAgent:
    def __init__(self, api_key):
        genai.configure(api_key=api_key)
        # Try to initialize with the search tool
        try:
            self.model_with_search = genai.GenerativeModel(
                model_name='gemini-1.5-flash',
                tools=[{"google_search_retrieval": {}}]
            )
        except:
            self.model_with_search = None
        
        # Fallback model without tools (always works)
        self.standard_model = genai.GenerativeModel(model_name='gemini-1.5-flash')

    def parse_cv(self, pdf_file):
        try:
            doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
            text = " ".join([page.get_text() for page in doc])
            prompt = f"Return JSON for CV: name, university, degree, skills. Text: {text}"
            response = self.standard_model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error: {str(e)}"

    def search_high_signal_leads(self, industry, location, profile):
        prompt = f"""
        Find 5 specific {industry} firms in {location} that would be good for an internship.
        Include: Company Name, Recent Activity, and Why they fit this profile: {profile}.
        Return as a clean list.
        """
        
        # Attempt 1: Search with Grounding
        if self.model_with_search:
            try:
                response = self.model_with_search.generate_content(prompt)
                return response.text
            except Exception:
                pass # Fall through to standard model if search fails
        
        # Attempt 2: Standard Model (Fallback)
        try:
            response = self.standard_model.generate_content(f"Provide a researched list of 5 {industry} firms in {location} for internship outreach. Format clearly. Context: {profile}")
            return f"Note: Standard AI Insight (Live Search currently limited for this account):\n\n{response.text}"
        except Exception as e:
            return f"Logic Error: {str(e)}"

    def generate_outreach(self, lead, profile):
        response = self.standard_model.generate_content(f"Draft a LinkedIn message for {lead} based on {profile}.")
        return response.text
