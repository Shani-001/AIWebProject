import json
import re
import time
import logging
from typing import Optional, Dict, Any
from config import settings

logger = logging.getLogger(__name__)


def call_groq_llm(
    prompt: str,
    system_prompt: str,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    max_retries: int = 3
) -> Optional[Dict[str, Any]]:
    """
    Calls the Groq API using JSON response format with exponential backoff on rate limits.
    """
    key = api_key or settings.GROQ_API_KEY
    if not key:
        logger.error("Groq API key not provided.")
        return None

    try:
        from groq import Groq
        client = Groq(api_key=key)
    except Exception as e:
        logger.error(f"Failed to initialize Groq client: {e}")
        return None

    selected_model = model or settings.GROQ_MODEL
    delay = 1.0

    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=selected_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                response_format={"type": "json_object"}
            )
            raw_content = response.choices[0].message.content
            if not raw_content:
                logger.warning("Empty response received from Groq.")
                return None

            # Clean potential surrounding code fences
            cleaned = raw_content.strip()
            if cleaned.startswith("```"):
                cleaned = re.sub(r"^```(?:json)?\n?", "", cleaned)
                cleaned = re.sub(r"\n?```$", "", cleaned)

            data = json.loads(cleaned)
            return data
        except Exception as e:
            err_str = str(e)
            logger.warning(f"Groq API attempt {attempt+1}/{max_retries} failed: {err_str}")
            if "rate_limit" in err_str.lower() or "429" in err_str:
                time.sleep(delay)
                delay *= 2
            else:
                if attempt == max_retries - 1:
                    logger.error(f"Groq API final failure: {e}")
                time.sleep(1)

    return None
