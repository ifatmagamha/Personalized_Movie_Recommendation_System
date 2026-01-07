from typing import Dict, Any, Optional
import json
import re
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from src.api.settings import settings
from src.llm.prompts import INTENT_PARSER_PROMPT

# 1. Initialize Gemini Flash 
def get_llm():
    if not settings.GOOGLE_API_KEY:
        raise ValueError("GOOGLE_API_KEY is missing")
    return ChatGoogleGenerativeAI(
        model="gemini-flash-latest",
        temperature=0.0, # Lower temperature for structural extraction
        google_api_key=settings.GOOGLE_API_KEY,
        convert_system_message_to_human=True
    )

def _extract_json(text: Any) -> str:
    # Handle list of parts if model returns it
    if isinstance(text, list):
        text = "".join([str(p.get("text", p)) if isinstance(p, dict) else str(p) for p in text])
    
    if not isinstance(text, str):
        text = str(text)

    # Remove markdown code blocks if present
    text = re.sub(r'```json\s*', '', text)
    text = re.sub(r'```\s*', '', text)
    
    # Extract structural JSON
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        return match.group(0)
    return text.strip()

def parse_mood_to_filters(query: str) -> Dict[str, Any]:
    """
    Translates a raw string ("mood") into a full structured intent object.
    Returns: { "intent": ..., "mood": ..., "constraints": {...}, "explanation": ... }
    """
    try:
        llm = get_llm()
        prompt = PromptTemplate.from_template(INTENT_PARSER_PROMPT)
        chain = prompt | llm
        
        response = chain.invoke({"query": query})
        content = _extract_json(response.content)
        
        obj = json.loads(content)
        
        # Enforce basic structure
        if "constraints" not in obj:
            obj["constraints"] = {}
        
        return obj
    except Exception as e:
        print(f"[ERROR] Intent parsing failed for '{query}': {e}")
        return {
            "intent": "explore",
            "mood": "neutral",
            "constraints": {},
            "explanation": "Based on your request."
        }
