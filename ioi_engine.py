import google.generativeai as genai
import fitz  # PyMuPDF

class IOIAgent:
    def __init__(self, api_key):
        try:
            # Key ki safai
            k = api_key.strip().strip('"').strip("'")
            genai.configure(api_key=k)
            
            # Hum 2-3 model names try karenge jo bhi aapke account par active ho
            self.model = None
            for model_name in ['gemini-1.5-flash', 'gemini-1.5-pro', 'models/gemini-1.5-flash']:
                try:
                    m = genai.GenerativeModel(model_name)
                    m.generate_content("hi") # Test call
                    self.model = m
                    break
                except:
                    continue
        except Exception as e:
            self.model = None

    def parse_cv(self, pdf_file):
        if not self.model: return "API Key not working or Model not found."
        try:
            doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
            text = " ".join([page.get_text() for page in doc])
            res = self.model.generate_content(f"Extract key skills from: {text[:5000]}")
            return res.text
        except: return "PDF Error."

    def search_high_signal_leads(self, industry, location, profile):
        if not self.model: return "Agent Error: Please check your Gemini API Key in Secrets."
        try:
            # Simple prompt for stability
            prompt = f"List 5 internship target firms for {industry} in {location}. Context: {profile}"
            res = self.model.generate_content(prompt)
            return res.text
        except Exception as e:
            return f"Search Error: {str(e)}"

    def generate_outreach(self, lead, profile):
        try:
            res = self.model.generate_content(f"Draft a short message for {lead} and {profile}")
            return res.text
        except: return "Error"
