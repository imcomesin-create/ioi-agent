import google.generativeai as genai
import fitz  # PyMuPDF
import json

class IOIAgent:
    def __init__(self, api_key):
        genai.configure(api_key=api_key)
        # Use 'gemini-1.5-flash' - this is the most compatible name
        self.model = genai.GenerativeModel(
            model_name='gemini-1.5-flash',
            tools=[{"google_search_retrieval": {}}]
        )

    def parse_cv(self, pdf_file):
        """Extracts and structures CV data."""
        try:
            doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
            text = " ".join([page.get_text() for page in doc])
            prompt = f"Extract into JSON: Full Name, University, Degree, Skills. Text: {text}"
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error: {str(e)}"

    def search_high_signal_leads(self, industry, location, profile):
        """Discovers companies using real-time Google Search grounding."""
        try:
            prompt = f"Find 5 {industry} firms in {location} with recent news. JSON list: company, signal, contact, score, why. Profile: {profile}"
            # The tool might fail in some regions/accounts
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            # Fallback: if search tool fails, try without it
            try:
                fallback_model = genai.GenerativeModel('gemini-1.5-flash')
                res = fallback_model.generate_content(f"List 5 well-known {industry} firms in {location} for internships. Format as JSON.")
                return f"Search tool unavailable. Here are general targets:\n\n{res.text}"
            except:
                return f"Internal Error: {str(e)}"

    def generate_outreach(self, lead, profile):
        prompt = f"Draft a short LinkedIn message for {lead} based on {profile}."
        response = self.model.generate_content(prompt)
        return response.text
