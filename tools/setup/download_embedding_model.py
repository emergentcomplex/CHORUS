# Filename: tools/setup/download_embedding_model.py
# 🔱 This script pre-downloads the sentence transformer model for baking into the Docker image.

from sentence_transformers import SentenceTransformer
import os

MODEL_NAME = 'all-MiniLM-L6-v2'
MODEL_PATH = '/app/models'

def main():
    """Downloads the specified model to the specified path."""
    print(f"--- Downloading SentenceTransformer model: {MODEL_NAME} ---")
    print(f"Target directory: {MODEL_PATH}")
    
    # This command downloads the model files and tokenizer to the specified path.
    SentenceTransformer(MODEL_NAME, cache_folder=MODEL_PATH)
    
    # THE DEFINITIVE FIX: To verify, we must load the model using the *name* and *cache_folder* again.
    # The library knows how to find the model within the cache structure it creates.
    try:
        SentenceTransformer(MODEL_NAME, cache_folder=MODEL_PATH)
        print("✅ Model downloaded and verified successfully.")
    except Exception as e:
        print(f"❌ Verification failed. Error loading model from cache {MODEL_PATH}: {e}")
        exit(1)

if __name__ == "__main__":
    main()