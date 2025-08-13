# Filename: chorus_engine/infrastructure/services/embedding_service.py
# 🔱 The CHORUS Oracle: An isolated, single-process embedding service.

import os
from flask import Flask, request, jsonify
from sentence_transformers import SentenceTransformer
import logging
import numpy as np

# Configure logging
logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

def create_app():
    """
    Application factory for the embedding service.
    Lazily loads the SentenceTransformer model to be compatible with Gunicorn.
    """
    app = Flask(__name__)
    
    # Lazy loading of the model. This will be loaded once per worker process.
    # Since we mandate --workers=1, this will be a singleton.
    try:
        # Using an explicit cache folder within the container
        model_cache_path = '/app/models'
        os.makedirs(model_cache_path, exist_ok=True)
        app.model = SentenceTransformer('all-MiniLM-L6-v2', cache_folder=model_cache_path)
        logger.info("✅ SentenceTransformer model loaded successfully.")
    except Exception as e:
        logger.error(f"❌ Failed to load SentenceTransformer model: {e}", exc_info=True)
        app.model = None

    @app.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint."""
        if app.model:
            return jsonify({"status": "healthy", "model_loaded": True}), 200
        else:
            return jsonify({"status": "unhealthy", "model_loaded": False}), 503

    @app.route('/embed', methods=['POST'])
    def embed():
        """
        Endpoint to generate embeddings for a list of texts.
        Expects a JSON payload: {"texts": ["text1", "text2", ...]}
        """
        if not app.model:
            return jsonify({"error": "Model not loaded"}), 503

        data = request.get_json()
        if not data or 'texts' not in data or not isinstance(data['texts'], list):
            return jsonify({"error": "Invalid request payload. Expected {'texts': [...]}"}), 400

        try:
            texts = data['texts']
            embeddings = app.model.encode(texts)
            # Convert numpy array to a list of lists for JSON serialization
            embeddings_list = embeddings.tolist() if isinstance(embeddings, np.ndarray) else embeddings
            return jsonify({"embeddings": embeddings_list}), 200
        except Exception as e:
            logger.error(f"Error during embedding generation: {e}", exc_info=True)
            return jsonify({"error": "Failed to generate embeddings"}), 500

    return app