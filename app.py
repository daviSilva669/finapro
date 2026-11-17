from flask import Flask
from database import init_db
from routes import main_bp


def create_app():
    app = Flask(__name__)
    init_db()
    app.register_blueprint(main_bp)
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
