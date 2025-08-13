# Filename: wsgi_embedder.py
# 🔱 WSGI entry point for the CHORUS Embedding Service (The Oracle).

from chorus_engine.infrastructure.services.embedding_service import create_app

app = create_app()