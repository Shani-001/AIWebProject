import json
import re
import time
import logging
from typing import Optional, Dict, Any
from config import settings

logger = logging.getLogger(__name__)


def call_gemini_llm(
    prompt: str,
    system_prompt: str,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    max_retries: int = 3
) -> Optional[Dict[str, Any]]:
    """
    Calls Google Gemini API configured for JSON output with rate limit handling.
    """
    key = api_key or settings.GEMINI_API_KEY
    if not key:
        logger.error("Gemini API key not provided.")
        return None

    try:
        import google.generativeai as genai
        genai.configure(api_key=key)
    except Exception as e:
        logger.error(f"Failed to configure Gemini client: {e}")
        return None

    selected_model_name = model or settings.GEMINI_MODEL
    delay = 1.0

    for attempt in range(max_retries):
        try:
            model_instance = genai.GenerativeModel(
                model_name=selected_model_name,
                system_instruction=system_prompt,
                generation_config={"response_mime_type": "application/json"}
            )
            response = model_instance.generate_content(prompt)
            raw_content = response.text
            if not raw_content:
                logger.warning("Empty response received from Gemini.")
                return None

            cleaned = raw_content.strip()
            if cleaned.startswith("```"):
                cleaned = re.sub(r"^```(?:json)?\n?", "", cleaned)
                cleaned = re.sub(r"\n?```$", "", cleaned)

            data = json.loads(cleaned)
            return data
        except Exception as e:
            err_str = str(e)
            logger.warning(f"Gemini API attempt {attempt+1}/{max_retries} failed: {err_str}")
            if "quota" in err_str.lower() or "429" in err_str or "exhausted" in err_str.lower():
                time.sleep(delay)
                delay *= 2
            else:
                if attempt == max_retries - 1:
                    logger.error(f"Gemini API final failure: {e}")
                time.sleep(1)

    return None
