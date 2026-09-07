import google.generativeai as genai
import fitz  # PyMuPDF
import json

class IOIAgent:
    def __init__(self, api_key):
        genai.configure(api_key=api_key)
        # Using gemini-1.5-flash as it has broader access to the search tool
        # Adding the 'models/' prefix ensures the SDK finds the resource
        self.model = genai.GenerativeModel(
            model_name='models/gemini-1.5-flash',
            tools=[{"google_search_retrieval": {}}]
        )

    def parse_cv(self, pdf_file):
        """Extracts and structures CV data."""
        try:
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
        except Exception as e:
            return f"Error parsing CV: {str(e)}"

    def search_high_signal_leads(self, industry, location, profile):
        """Discovers companies using real-time Google Search grounding."""
        try:
            prompt = f"""
            Act as a Finance & Consulting Headhunter.
            Search for {industry} firms in {location}.
            Identify 5 specific firms that have RECENT 'Opportunity Signals' (fundraising, new office, acquisitions).
            Candidate Profile Context: {profile}

            Return a JSON list of objects with: company, signal, contact, score (0-100), why.
            """
            # Using generate_content with the grounded search tool
            response = self.model.generate_content(prompt)
            
            if response.text:
                return response.text
            else:
                return "No results found. Try adjusting your search criteria."
        except Exception as e:
            return f"Search Error: {str(e)}"

    def generate_outreach(self, lead, profile):
        """Generates personalized outreach."""
        try:
            prompt = f"""
            Write a concise LinkedIn connection request (max 300 chars) for:
            Target: {lead}
            Candidate Background: {profile}
            - Refer specifically to their recent activity.
            - Brief and professional.
            """
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error generating outreach: {str(e)}"
