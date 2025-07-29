# Filename: chorus_engine/adapters/llm/gemini_adapter.py (API Corrected)
#
# 🔱 CHORUS Autonomous OSINT Engine
#
# This file contains the concrete adapter for the Google Gemini LLM.

import os
import time
import logging
from typing import Optional

import google.generativeai as genai
from google.generativeai import types
from dotenv import load_dotenv

from chorus_engine.app.interfaces import LLMInterface

class GeminiAdapter(LLMInterface):
    """A concrete adapter for the Google Gemini LLM."""

    def __init__(self):
        """Initializes the Gemini client."""
        load_dotenv()
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables.")
        
        try:
            # The client is configured once for the application instance.
            genai.configure(api_key=api_key)
            logging.info("GeminiAdapter initialized successfully.")
        except Exception as e:
            logging.error(f"Failed to initialize Gemini client: {e}")
            raise

    def instruct(self, prompt: str, model_name: str, attempt: int = 1, max_retries: int = 3) -> Optional[str]:
        """
        Sends a prompt to the specified Gemini model and returns the text response.
        Implements an exponential backoff retry mechanism.
        """
        if attempt > max_retries:
            logging.error(f"LLM call failed after {max_retries} attempts.")
            return None

        logging.info(f"Sending prompt to model '{model_name}' (Attempt {attempt}/{max_retries})...")
        try:
            # DEFINITIVE FIX: Instantiate the model directly and call generate_content.
            model = genai.GenerativeModel(model_name)
            
            generation_config = types.GenerationConfig(
                temperature=0.0, 
                top_p=1.0, 
                max_output_tokens=8192
            )
            response = model.generate_content(
                contents=prompt, 
                generation_config=generation_config
            )
            return response.text
        except Exception as e:
            wait_time = 5 * (2 ** (attempt - 1))
            logging.warning(f"LLM call failed on attempt {attempt}: {e}. Retrying in {wait_time} seconds...")
            time.sleep(wait_time)
            return self.instruct(prompt, model_name, attempt + 1, max_retries)
