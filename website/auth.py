from flask import Blueprint, session, redirect
from authlib.integrations.flask_client import OAuth
from . import oauth
import os

auth = Blueprint("auth", __name__)


@auth.route("/login")
def login():
    return oauth.auth0.authorize_redirect(redirect_uri=os.getenv("AUTH0_CALLBACK_URL"))


@auth.route("/callback")
def callback():
    token = oauth.auth0.authorize_access_token()
    userinfo = oauth.auth0.get("userinfo").json()
    session["user"] = {
        "name": userinfo["name"],
        "email": userinfo["email"],
        "picture": userinfo["picture"],
    }
    return redirect("/")


@auth.route("/logout")
def logout():
    session.clear()
    return redirect(
        f"https://{os.getenv('AUTH0_DOMAIN')}/v2/logout?returnTo=http://localhost:5000&client_id={os.getenv('AUTH0_CLIENT_ID')}"
    )
