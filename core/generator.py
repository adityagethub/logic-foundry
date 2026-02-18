import google.generativeai as genai
from openai import OpenAI
import json
# Reusing keys from extractor
from core.extractor import OPENROUTER_API_KEY

def generate_modern_code(logic_json, target_language, api_keys_input, model_name):
    """
    Generates modern, idiomatic code in the target_language based on the extracted business logic.
    """
    
    # Determine keys to use (Input overrides hardcoded)
    # In this OpenRouter version, we only use the OpenRouter key
    openrouter_key = api_keys_input.get("OPENROUTER_API_KEY") or OPENROUTER_API_KEY

    system_prompt = f"""You are a Clean Code Expert. I will give you a list of Business Rules in JSON format.
Your goal is to implement these rules in highly readable, idiomatic {target_language} code.

CRITICAL INSTRUCTIONS:
- DO NOT look at any original legacy code (none is provided, only rules).
- Use modern patterns appropriate for {target_language}. 
  - If Python, use type hinting, dataclasses, and docstrings.
  - If Java, use Streams, Records, and Optional where appropriate.
  - If TypeScript, use interfaces and strict types.
- Add comments linking specific lines of code to the Rule IDs (e.g., // Implements rule_5).
- Ensure all logic paths from the JSON are covered.
- Return ONLY the code block. Do not wrap in markdown code fences if possible, or if you do, ensure it's clean.
"""

    user_prompt = f"Business Rules to Implement:\n\n{json.dumps(logic_json, indent=2)}"

    try:
         # Initialize OpenAI client pointing to OpenRouter
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=openrouter_key,
            default_headers={
                "HTTP-Referer": "http://localhost:8501", 
                "X-Title": "Logic Foundry", 
            }
        )

        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        content = response.choices[0].message.content
        # Clean up markdown if present
        if content.startswith("```"):
            lines = content.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines[-1].startswith("```"):
                lines = lines[:-1]
            content = "\n".join(lines)
        return content
    except Exception as e:
        return f"# Error generating code with OpenRouter: {str(e)}"
