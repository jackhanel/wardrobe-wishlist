from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
from authlib.integrations.flask_client import OAuth

db = SQLAlchemy()


def create_app():
    load_dotenv()

    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_DATABASE_URI")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    oauth = OAuth(app)
    auth0 = oauth.register(
        'auth0',
        client_id=os.getenv("AUTH0_CLIENT_ID"),
        client_secret=os.getenv("AUTH0_CLIENT_SECRET"),
        api_base_url=f"https://{os.getenv('AUTH0_DOMAIN')}",
        access_token_url=f"https://{os.getenv('AUTH0_DOMAIN')}/oauth/token",
        authorize_url=f"https://{os.getenv('AUTH0_DOMAIN')}/authorize",
        client_kwargs={'scope': 'openid profile email'},
    )

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")

    with app.app_context():
        db.create_all()

    return app
