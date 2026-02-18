import os
import json
from openai import OpenAI
# Reusing keys from extractor
from core.extractor import OPENROUTER_API_KEY

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY", OPENROUTER_API_KEY),
)

def validate_equivalence(original_logic_json, modern_code_text, model_name="anthropic/claude-3.5-sonnet"):
    """
    Asks the AI to perform a symbolic equivalence check between the extracted logic rules
    and the generated modern code.
    """
    
    # robustly handle string vs dict input
    if isinstance(original_logic_json, str):
        rules_str = original_logic_json
    else:
        rules_str = json.dumps(original_logic_json, indent=2)

    system_prompt = """
    You are a Formal Verification Engine. Your goal is to mathematically verify that a piece of Modern Code 
    perfectly implements a set of Legacy Business Rules.

    I will provide:
    1. THE TRUTH: A JSON list of business rules extracted from legacy code.
    2. THE IMPLEMENTATION: A snippet of modern code.

    YOUR TASK:
    Perform a symbolic execution audit. Compare every branch, threshold (>, >=), and return value.
    
    Output a strict JSON report in this format:
    {
        "score": (integer 0-100),
        "status": "PASS" | "FAIL" | "WARNING",
        "summary": "One sentence summary of the verification.",
        "discrepancies": [
            { "rule_id": "rule_X", "severity": "CRITICAL" | "MINOR", "issue": "Description of the mismatch (e.g. Code uses > 50, Rule says >= 50)" }
        ]
    }
    
    If the code is perfect, "discrepancies" should be empty and score should be 100.
    """

    user_prompt = f"""
    --- THE TRUTH (Logic Rules) ---
    {rules_str}

    --- THE IMPLEMENTATION (Modern Code) ---
    {modern_code_text}
    """

    try:
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
            "score": 0, 
            "status": "ERROR", 
            "summary": f"Validation failed to run: {str(e)}", 
            "discrepancies": []
        }
