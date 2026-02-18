import json
import google.generativeai as genai
from openai import OpenAI
import streamlit as st
import os

# HARDCODED KEYS (Replace with real keys or use env vars)
# User: Paste your OpenRouter "Key for Model Requests" here
api_key = st.secrets.get("OPENROUTER_API_KEY", os.getenv("OPENROUTER_API_KEY"))

def extract_logic(code_text, model_name):
    """
    Extracts business logic from code_text using the specified model via OpenRouter.
    Returns a parsed JSON dictionary.
    """
    
    # System prompt to enforce JSON structure
    system_prompt = """You are an expert logic extractor. Your goal is to extract business logic from the provided code and return it in the following JSON structure:
{
  "module_name": "string",
  "stats": { 
    "complexity_score": 1-10, 
    "rule_count": int 
  },
  "rules": [ 
    { 
      "id": "rule_1", 
      "trigger": "if condition...", 
      "action": "then...", 
      "reason": "why" 
    } 
  ]
}
CRITICAL INSTRUCTIONS:
1. You MUST map EVERY exhaust path and else-condition. Do not summarize or skip default fallbacks.
2. For "else" blocks, create a specific rule with a trigger like "ELSE" or "OTHERWISE".
3. Return ONLY valid JSON. Do not include markdown formatting like ```json."""

    user_prompt = f"Code to analyze:\n\n{code_text}"

    try:
        # Initialize OpenAI client pointing to OpenRouter
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=OPENROUTER_API_KEY,
            default_headers={
                "HTTP-Referer": "http://localhost:8501", # Optional
                "X-Title": "Logic Foundry", # Optional
            }
        )
        
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            # Helper to ensure JSON if model supports it (optional, removing for broad compatibility)
            # response_format={"type": "json_object"} 
        )
        
        content = response.choices[0].message.content.strip()
        
        # Clean up potential markdown
        if content.startswith("```json"):
            content = content[7:]
        elif content.startswith("```"):
            content = content[3:]
            
        if content.endswith("```"):
            content = content[:-3]
            
        return json.loads(content.strip())
        
    except Exception as e:
        return {
            "error": f"OpenRouter extraction failed: {str(e)}",
            "rules": [],
            "module_name": "Error",
            "stats": {"complexity_score": 0, "rule_count": 0}
        }
