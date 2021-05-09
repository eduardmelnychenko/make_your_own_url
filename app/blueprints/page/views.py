from flask import Blueprint, render_template, request, redirect, url_for

import app.engine.url_model
from app.db.db_procs import log_click
from app.etl.tracker import get_user_info

page = Blueprint('page', __name__, template_folder='templates')

from flask_login import (
    current_user,
)


@page.route('/', methods=['GET', 'POST'])
def index():
    if current_user.is_authenticated:
        return redirect(url_for('user.home'))

    short_url = None
    long_url = None
    new_url = True
    show_warning = False
    show_error = False

    if request.method == 'POST':
        long_url = request.form['longUrlInput']
        print(long_url)
        """
        Default behaviour is to assume that long url to be incorrect and show warning. Only if it passes validation, 
        proceeds to show short url.
        """
        show_warning = True

        nu = app.engine.url_model.Url()
        outcome_success = nu.create_url(long_url)
        short_url = nu.short_url
        if outcome_success:
            new_url = False
            show_warning = False

    return render_template('index.html', short_url=short_url, long_url=long_url,
                           new_url=new_url, show_warning=show_warning, show_error=show_error, is_auth=False)


@page.route('/signup')
def signup():
    return render_template('signup.html')


@page.route('/about')
def about():
    return render_template('about.html')


@page.route('/terms')
def terms():
    return render_template('terms.html')


@page.route('/privacy')
def privacy():
    return render_template('privacy.html')


@page.route('/not_found', methods=['GET'])
def not_found():
    return render_template('404.html', code=404)


@page.route('/<string:suffix>', methods=['GET'])
def url_redirect(suffix):
    long_url = app.engine.url_model.Url().match_long_url(suffix)

    print(long_url)
    if long_url == '404':
        return redirect(url_for('page.not_found'))

    if long_url:
        click_source = get_user_info()
        log_click(suffix, click_source)
        return redirect(long_url, code=302)

    return render_template('index.html', short_url=None, long_url=None, new_url=True, show_error=True)
