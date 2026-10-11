import os
from dotenv import load_dotenv
from app import create_app

# Load environment configuration
load_dotenv()

env = os.getenv("FLASK_ENV", "development")
app = create_app(env)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "1") == "1"
    print(f" * Starting CRMS Backend on http://127.0.0.1:{port}")
    print(f" * API Documentation available at http://127.0.0.1:{port}/docs/")
    app.run(host="0.0.0.0", port=port, debug=debug)
