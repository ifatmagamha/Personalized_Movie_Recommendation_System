from typing import Dict, List
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from src.api.settings import settings
from src.llm.prompts import REASONING_PROMPT

def get_llm():
    if not settings.GOOGLE_API_KEY:
        return None
    return ChatGoogleGenerativeAI(
        model="gemini-flash-latest",
        temperature=0.7, 
        google_api_key=settings.GOOGLE_API_KEY
    )

def generate_reason(user_history: List[str], candidate_title: str, candidate_genres: str) -> str:
    """
    Generates a personalized 1-sentence explanation.
    """
    try:
        llm = get_llm()
        if not llm:
            return "Personalized recommendation."

        prompt = PromptTemplate.from_template(REASONING_PROMPT)
        chain = prompt | llm
        
        hist_str = ", ".join(user_history[:3]) # Only use top 3 recently liked
        
        response = chain.invoke({
            "user_history": hist_str, 
            "candidate_title": candidate_title,
            "candidate_genres": candidate_genres
        })
        
        return response.content.strip()
    except Exception as e:
        print(f"[WARN] Reasoning failed: {e}")
        return "Based on your taste."
