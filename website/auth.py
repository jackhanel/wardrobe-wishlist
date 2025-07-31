from flask import Blueprint, session, redirect
from authlib.integrations.flask_client import OAuth
from . import oauth, db
from .models import User
import os

auth = Blueprint("auth", __name__)


@auth.route("/login")
def login():
    return oauth.auth0.authorize_redirect(redirect_uri=os.getenv("AUTH0_CALLBACK_URL"))


@auth.route("/callback")
def callback():
    token = oauth.auth0.authorize_access_token()
    userinfo = oauth.auth0.userinfo()

    auth0_id = userinfo["sub"]
    user = User.query.filter_by(auth0_id=auth0_id).first()
    if not user:
        user = User(auth0_id=auth0_id, email=userinfo["email"], name=userinfo["name"])
        db.session.add(user)
        db.session.commit()

    session["user"] = {
        "id": user.id,
        "auth0_id": auth0_id,
        "name": user.name,
        "email": user.email,
    }

    return redirect("/")


@auth.route("/logout")
def logout():
    session.clear()
    return redirect(
        f"https://{os.getenv('AUTH0_DOMAIN')}/v2/logout?returnTo=https://wardrobe-wishlist.onrender.com&client_id={os.getenv('AUTH0_CLIENT_ID')}"
    )
