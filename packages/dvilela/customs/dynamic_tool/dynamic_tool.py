"""Contains the job definitions"""

import re
from typing import Any, Dict, Optional, Tuple

import google.generativeai as genai

DEFAULT_TEMPERATURE = 1.5

PROMPT = """
Create a Python function called 'dynamic_function' that implements the following logic:

{user_prompt}

The function receives the following arguments: {kwargs}

Only respond with the Python code.
Do not include markdown syntax.
"""


def error_response(msg: str) -> Tuple[str, None, None, None]:
    """Return an error mech response."""
    return msg, None, None, None


def clean_code(code):
    """Clean code"""
    match = re.search(r"```python\n(.*?)\n```", code, re.DOTALL)
    return match.group(1) if match else code


def evaluate_code(code, **kwargs):
    """Dynamically evaluates a function defined as a string"""

    print("--------------------------------------------")
    print(f"Evaluating the following function:\n{code}\n")
    print(f"kwargs = {kwargs}")

    try:
        local_scope = {}
        exec(code, {}, local_scope)
        result = local_scope.get("dynamic_function")(**kwargs)
        print(f"Result = {result}")
        return result
    except Exception as e:
        print(f"An exception occured while evaluating the code: {e}")
        return None
    finally:
        print("--------------------------------------------")


def run(**kwargs) -> Tuple[Optional[str], Optional[Dict[str, Any]], Any, Any]:
    """Run the task"""

    GEMINI_API_KEY = kwargs.get("api_keys", {}).get("gemini", None)
    if not GEMINI_API_KEY:
        return error_response("GEMINI_API_KEY was not provided")

    genai.configure(api_key=GEMINI_API_KEY)

    model_name = kwargs.get("model", "gemini-2.0-flash")
    model = genai.GenerativeModel(model_name)
    generation_config_kwargs = {
        "temperature": kwargs.get("temperature", DEFAULT_TEMPERATURE)
    }
    user_prompt = kwargs.get("prompt", None)
    if not user_prompt:
        return error_response("Prompt was not provided")

    function_kwargs = kwargs.get("function_kwargs", {})

    try:
        response = model.generate_content(
            PROMPT.format(
                user_prompt=user_prompt, kwargs=tuple(function_kwargs.keys())
            ),
            generation_config=genai.types.GenerationConfig(
                **generation_config_kwargs,
            ),
        )
    except Exception as e:
        return error_response(f"Gemini request failed: {e}")

    code = clean_code(response.text)
    result = evaluate_code(code, **function_kwargs)

    if result is None:
        return error_response(f"Code evaluation produced an exception:\n{code}")

    return result, None, None, None
