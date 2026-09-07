import google.generativeai as genai
import fitz  # PyMuPDF

class IOIAgent:
    def __init__(self, api_key):
        try:
            # Clean the key (remove any accidental spaces or quotes)
            clean_key = api_key.strip().replace('"', '').replace("'", "")
            genai.configure(api_key=clean_key)
            # Use the most basic, universal model name
            self.model = genai.GenerativeModel('gemini-1.5-flash')
        except Exception as e:
            self.model = None
            print(f"Initialization Error: {e}")

    def parse_cv(self, pdf_file):
        if not self.model: return "API Key Error: Model not initialized."
        try:
            doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
            text = " ".join([page.get_text() for page in doc])
            response = self.model.generate_content(f"Extract Name, University, and Skills from this CV: {text}")
            return response.text
        except Exception as e:
            return f"CV Error: {str(e)}"

    def search_high_signal_leads(self, industry, location, profile):
        if not self.model: return "API Key Error: Please check your Gemini Key in Streamlit Secrets."
        
        # We removed the 'tools' parameter to ensure the API key is accepted
        prompt = f"""
        List 5 real and well-known {industry} firms in {location} for an internship.
        For each, explain why they are a good target for a student with this profile: {profile}.
        Provide the response in a professional list format.
        """
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"API Key Error: Google returned an error. This usually means your API Key is invalid or restricted. Error: {str(e)}"

    def generate_outreach(self, lead, profile):
        if not self.model: return "API Key Error."
        response = self.model.generate_content(f"Write a 1-sentence LinkedIn hook for {lead} based on {profile}.")
        return response.text
