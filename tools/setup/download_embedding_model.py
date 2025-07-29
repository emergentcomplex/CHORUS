# Filename: tools/setup/download_embedding_model.py
# A one-time script to download the sentence-transformer model to a local directory.

from sentence_transformers import SentenceTransformer
from chorus_engine.config import MODEL_DIR

MODEL_NAME = 'all-mpnet-base-v2'
LOCAL_MODEL_PATH = MODEL_DIR / MODEL_NAME

def main():
    """Downloads and saves the model."""
    print(f"[*] Downloading embedding model '{MODEL_NAME}'...")
    print(f"[*] This may take a few minutes depending on your connection.")
    
    MODEL_DIR.mkdir(exist_ok=True)
    model = SentenceTransformer(MODEL_NAME)
    model.save(str(LOCAL_MODEL_PATH))
    
    print(f"\n✅ Model downloaded successfully and saved to: {LOCAL_MODEL_PATH}")

if __name__ == "__main__":
    from chorus_engine.config import setup_path
    setup_path()
    main()
