# Filename: wsgi.py
#
# 🔱 CHORUS WSGI Entrypoint
# This is the canonical entry point for the Gunicorn server. It ensures
# that the Flask application is discovered and loaded correctly.

from chorus_engine.infrastructure.web.web_ui import app

if __name__ == "__main__":
    app.run()