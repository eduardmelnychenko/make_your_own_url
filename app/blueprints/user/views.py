import requests
import json
from flask import Blueprint, render_template, request, redirect, current_app, url_for, flash

import app.engine.url_model
from app.engine.user_model import User
from app.engine.validators import *
from app_run import application

from flask_login import (
    current_user,
    login_required,
    login_user,
    logout_user,
)

from oauthlib.oauth2 import WebApplicationClient

user = Blueprint('user', __name__, template_folder='templates')

with application.app_context():
    GOOGLE_CLIENT_ID = current_app.config.get('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = current_app.config.get('GOOGLE_CLIENT_SECRET')
    client = WebApplicationClient(GOOGLE_CLIENT_ID)


def get_google_provider_cfg():
    with application.app_context():
        google_discovery_url = current_app.config.get('GOOGLE_DISCOVERY_URL')
    return requests.get(google_discovery_url).json()


@user.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    short_url = None
    long_url = None
    new_url = True
    show_warning = False
    show_error = False
    cu = User(current_user.id)

    if not cu.is_authenticated:
        return redirect(url_for('page.index'))

    url_table_data = cu.get_top_user_urls()

    clicks_table_data = cu.get_most_clicked_urls()

    if request.method == 'POST':
        for key in request.form:
            print(key, request.form[key])

        long_url = request.form.get('longUrlInput')
        description = request.form.get('urlDescription', '')
        custom_suffix = request.form.get('customSuffix')
        days_to_live = request.form.get('urlDaysLive', None)

        print(long_url, description, custom_suffix, days_to_live)

        """
        Default behaviour is to assume that long url to be incorrect and show warning. Only if it passes validation, 
        proceeds to show short url.
        """
        show_warning = True

        days_to_live = validate_exp_date(days_to_live)

        custom_suffix = validate_suffix(custom_suffix)

        nu = app.engine.url_model.Url(current_user=cu, suffix=custom_suffix)
        nu.print_info()

        outcome_success = nu.create_url(long_url=long_url, description=description,
                                        days_to_live=days_to_live)
        nu.print_info()

        short_url = nu.short_url

        if outcome_success:
            new_url = False
            show_warning = False

    return render_template('home.html', short_url=short_url, long_url=long_url, url_table_data=url_table_data,
                           clicks_table_data=clicks_table_data,
                           new_url=new_url, show_warning=show_warning, show_error=show_error)


@user.route('/urls', methods=['GET', 'POST'])
@login_required
def urls():
    show_warning = False
    show_error = False
    cu = User(current_user.id)
    all_url_table = cu.get_user_url_table()
    return render_template('urls.html', all_url_table=all_url_table, show_warning=show_warning, show_error=show_error)


@user.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    return render_template('settings.html')


@user.route('/delete_account', methods=['GET', 'POST'])
@login_required
def delete_account():
    res = User(current_user.id).drop_user()
    if res is True:
        logout_user()
        flash('Your account was successfully deleted', 'success')
        return redirect(url_for('page.index'))
    else:
        logout_user()
        flash('Error! Try again later!', 'danger')
        return redirect(url_for('page.index'))


@user.route("/login")
def login():
    # Find out what URL to hit for Google login
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Use library to construct the request for Google login and provide
    # scopes that let you retrieve user's profile from Google
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)


@user.route("/login/callback")
def callback():
    # Get authorization code Google sent back to you
    code = request.args.get("code")

    # Find out what URL to hit to get tokens that allow you to ask for
    # things on behalf of a user
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]

    # Prepare and send a request to get tokens! Yay tokens!
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

    # Parse the tokens!
    client.parse_request_body_response(json.dumps(token_response.json()))

    # Now that you have tokens (yay) let's find and hit the URL
    # from Google that gives you the user's profile information,
    # including their Google profile image and email
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    # You want to make sure their email is verified.
    # The user authenticated with Google, authorized your
    # app, and now you've verified their email through Google!
    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        picture = userinfo_response.json()["picture"]
        users_name = userinfo_response.json()["given_name"]
    else:
        return "User email not available or not verified by Google.", 400

    # Create a user in your db with the information provided
    # by Google
    google_user = User(
        id_=unique_id, name=users_name, email=users_email, profile_pic=picture
    )

    # Doesn't exist? Add it to the database.
    if not User(unique_id).get():
        u = User(unique_id, users_name, users_email, picture)
        u.create()
        return redirect(url_for("page.signup"))

    # Begin user session by logging the user in
    login_user(google_user)

    # Send user back to homepage
    return redirect(url_for("user.home"))


@user.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("page.index"))
