"""Contains the job definitions"""

import os
import re
from typing import Any, Dict, Optional, Tuple

import google.generativeai as genai

DEFAULT_MODEL = "gemini-2.0-flash"
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


def dynamic_tool(
    user_prompt: str,
    function_kwargs: dict,
    gemini_api_key: str,
    model_name: str = DEFAULT_MODEL,
    temperature: float = DEFAULT_TEMPERATURE,
):
    """
    A tool that dynamically creates and evaluates LLM-generated code.

    user_prompt: a description of a function to be dynamically implemented by the LLM
    function_kwargs: the keyword argument the generated function is expected to take
    gemini_api_key: API key for Gemini
    model_name: the LLM model's name
    temperature: the LLM model's temperature
    """

    genai.configure(api_key=gemini_api_key)

    model = genai.GenerativeModel(model_name)
    generation_config_kwargs = {"temperature": temperature}

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
        print(f"Gemini request failed: {e}")
        return None

    code = clean_code(response.text)
    return evaluate_code(code, **function_kwargs)


def run(**kwargs) -> Tuple[Optional[str], Optional[Dict[str, Any]], Any, Any]:
    """Run the task"""

    gemini_api_key = kwargs.get("api_keys", {}).get(
        "gemini", os.environ.get("GEMINI_API_KEY")
    )
    if not gemini_api_key:
        return error_response("gemini_api_key was not provided")

    model_name = kwargs.get("model", DEFAULT_MODEL)
    temperature = kwargs.get("temperature", DEFAULT_TEMPERATURE)
    user_prompt = kwargs.get("prompt", None)
    if not user_prompt:
        return error_response("Prompt was not provided")
    function_kwargs = kwargs.get("function_kwargs", {})

    result = dynamic_tool(
        user_prompt, function_kwargs, gemini_api_key, model_name, temperature
    )

    if result is None:
        return error_response("Code evaluation produced an exception")

    return result, None, None, None
