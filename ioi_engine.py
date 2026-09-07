import groq
import fitz  # PyMuPDF
import os

class IOIAgent:
    def __init__(self, api_key):
        try:
            # Groq Client setup
            self.client = groq.Groq(api_key=api_key.strip().strip('"'))
            self.model = "llama3-8b-8192" # Fast and accurate
        except Exception as e:
            self.client = None
            print(f"Init Error: {e}")

    def parse_cv(self, pdf_file):
        if not self.client: return "API Key missing."
        try:
            doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
            text = " ".join([page.get_text() for page in doc])
            chat_completion = self.client.chat.completions.create(
                messages=[{"role": "user", "content": f"Summarize this CV briefly: {text[:5000]}"}],
                model=self.model,
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            return f"CV Error: {e}"

    def search_high_signal_leads(self, industry, location, profile):
        if not self.client: return "Check your Groq Key in Secrets."
        try:
            prompt = f"List 5 internship targets in {industry} in {location} for this student: {profile}. Be specific."
            chat_completion = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=self.model,
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            return f"Model Error: {str(e)}"

    def generate_outreach(self, lead, profile):
        try:
            res = self.client.chat.completions.create(
                messages=[{"role": "user", "content": f"Write a 1-sentence LinkedIn hook for {lead} and {profile}"}],
                model=self.model,
            )
            return res.choices[0].message.content
        except:
            return "Error generating message."
