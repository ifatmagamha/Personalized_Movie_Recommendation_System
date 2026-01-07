import os
import google.generativeai as genai
from src.api.settings import settings

def test_gemini():
    api_key = settings.GOOGLE_API_KEY
    if not api_key:
        print("No API Key found")
        return
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-flash-latest')
    try:
        response = model.generate_content("Say hello")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_gemini()
