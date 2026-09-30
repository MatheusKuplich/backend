import os

from flask import Flask

from config import INSTANCE_DIR, Config


def create_app():
    os.makedirs(INSTANCE_DIR, exist_ok=True)

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    # Initialize database
    from database import engine, Base
    from models import Categoria, Produto, Cliente  # noqa: F401
    
    Base.metadata.create_all(engine)

    from app.routes import bp as api_bp, paginas as paginas_bp, admin as admin_bp

    app.register_blueprint(api_bp)
    app.register_blueprint(paginas_bp)
    app.register_blueprint(admin_bp)

    return app
