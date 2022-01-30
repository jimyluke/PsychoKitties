"""App entry point."""
from application import init_app

if __name__ == "__main__":
    app = init_app()
    app.run(host="0.0.0.0", port=5000)
