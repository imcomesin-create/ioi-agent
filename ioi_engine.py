import google.generativeai as genai
import fitz  # PyMuPDF

class IOIAgent:
    def __init__(self, api_key):
        try:
            # Clean the key
            clean_key = api_key.strip().replace('"', '').replace("'", "")
            genai.configure(api_key=clean_key)
            
            # TRIPLE FALLBACK STRATEGY
            # We try three different model names to ensure compatibility
            self.model_names = ['gemini-1.5-flash-latest', 'gemini-1.5-pro-latest', 'gemini-pro']
            self.model = None
            
            for name in self.model_names:
                try:
                    test_model = genai.GenerativeModel(name)
                    # Test if the model actually responds
                    test_model.generate_content("health check")
                    self.model = test_model
                    print(f"Success: Using {name}")
                    break
                except:
                    continue
                    
        except Exception as e:
            self.model = None

    def parse_cv(self, pdf_file):
        if not self.model: return "API Key Error: Could not initialize any Gemini model."
        try:
            doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
            text = " ".join([page.get_text() for page in doc])
            response = self.model.generate_content(f"Summarize this CV briefly: {text}")
            return response.text
        except Exception as e:
            return f"CV Error: {str(e)}"

    def search_high_signal_leads(self, industry, location, profile):
        if not self.model: return "API Key Error: Check your Gemini Key in Streamlit Secrets."
        
        prompt = f"""
        List 5 real and well-known {industry} firms in {location} for an internship.
        Candidate background: {profile}.
        Provide a professional list.
        """
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"The AI could not process this search. Please ensure your API key is from the 'Free Tier' and is active. Error: {str(e)}"

    def generate_outreach(self, lead, profile):
        if not self.model: return "Error"
        response = self.model.generate_content(f"Short LinkedIn hook for {lead} and {profile}.")
        return response.text
