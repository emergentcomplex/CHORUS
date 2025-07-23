# Filename: scripts/download_embedding_model.py
# A one-time script to download the sentence-transformer model to a local directory.

from sentence_transformers import SentenceTransformer
import os

# Define the model name and the local path where it will be saved.
MODEL_NAME = 'all-mpnet-base-v2'
LOCAL_MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'models', MODEL_NAME)

def main():
    """Downloads and saves the model."""
    print(f"[*] Downloading embedding model '{MODEL_NAME}'...")
    print(f"[*] This may take a few minutes depending on your connection.")
    
    # The .save() method handles the download and saves all necessary files.
    model = SentenceTransformer(MODEL_NAME)
    model.save(LOCAL_MODEL_PATH)
    
    print(f"\n✅ Model downloaded successfully and saved to: {LOCAL_MODEL_PATH}")
    print("   You can now point all scripts to this local path.")

if __name__ == "__main__":
    main()
