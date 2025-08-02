# Filename: chorus_engine/adapters/llm/gemini_adapter.py (Definitively Corrected)
#
# 🔱 CHORUS Autonomous OSINT Engine
#
# This file contains the concrete adapter for the Google Gemini LLM.

import os
import time
import logging
import random
from typing import Optional

import google.generativeai as genai
from google.api_core import exceptions as google_exceptions
# THE DEFINITIVE FIX: Do not import load_dotenv here.

from chorus_engine.app.interfaces import LLMInterface

log = logging.getLogger(__name__)

class GeminiAdapter(LLMInterface):
    """A concrete adapter for the Google Gemini LLM."""

    def __init__(self):
        """Initializes the Gemini client and retry configuration."""
        # This adapter no longer loads the environment. It depends on the
        # application entry point to have already done so.
        self._is_configured = False
        api_key = os.getenv("GOOGLE_API_KEY")
        
        if not api_key:
            log.warning("GOOGLE_API_KEY not found. GeminiAdapter will be non-functional.")
        else:
            try:
                genai.configure(api_key=api_key)
                self._is_configured = True
                log.info("GeminiAdapter initialized and configured successfully.")
            except Exception as e:
                log.error(f"Failed to configure Gemini client: {e}")

        self.max_retries = int(os.getenv("LLM_MAX_RETRIES", 5))
        self.base_backoff = float(os.getenv("LLM_BASE_BACKOFF", 2.0))

    def is_configured(self) -> bool:
        return self._is_configured

    def instruct(self, prompt: str, model_name: str) -> Optional[str]:
        if not self.is_configured():
            log.error("LLM call failed: Adapter is not configured. Check API key.")
            return None

        for attempt in range(self.max_retries):
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(contents=prompt)
                return response.text
            except (google_exceptions.ResourceExhausted, 
                    google_exceptions.ServiceUnavailable) as e:
                if attempt < self.max_retries - 1:
                    delay = self.base_backoff * (2 ** attempt) + random.uniform(0, 1)
                    log.warning(f"LLM call failed with retryable error: {e}. Retrying in {delay:.2f} seconds...")
                    time.sleep(delay)
                else:
                    log.error(f"LLM call failed after {self.max_retries} attempts. Final error: {e}")
                    return None
            except Exception as e:
                log.error(f"LLM call failed with a non-retryable error: {e}", exc_info=True)
                return None
        return None
