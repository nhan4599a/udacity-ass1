"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import render_template, flash, redirect, request, session, url_for
from werkzeug.urls import url_parse
from config import Config
from FlaskWebProject import app, db
from FlaskWebProject.forms import LoginForm, PostForm, RegisterForm
from flask_login import current_user, login_user, logout_user, login_required
from FlaskWebProject.models import User, Post, UserProvider
import msal
import uuid
from FlaskWebProject.helper import get_form_values

IMAGE_SOURCE_URL = f'https://{app.config["BLOB_ACCOUNT"]}.blob.core.windows.net/{app.config["BLOB_CONTAINER"]}/'

@app.route('/')
@app.route('/home')
@login_required
def home():
    posts = Post.query.filter_by(user_id=current_user.id)
    return render_template(
        'index.html',
        username=current_user.username,
        title='Home Page',
        posts=posts
    )


@app.route('/new_post', methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post()
        post.save_changes(form, request.files['image_path'], current_user.id, new=True)
        return redirect(url_for('home'))
    return render_template(
        'post.html',
        title='Create Post',
        username=current_user.username,
        imageSource=IMAGE_SOURCE_URL,
        form=form
    )


@app.route('/post/<id>', methods=['GET', 'POST', 'DELETE'])
@login_required
def post(id):
    post = Post.query.filter_by(id=id).first()
    if (post is None):
        return '', 404
    
    if (request.method == 'DELETE'):
        db.session.delete(post)
        db.session.commit()
        return '', 200
    
    form = PostForm(formdata=request.form, obj=post)
    if form.validate_on_submit():
        post.save_changes(form, request.files['image_path'], current_user.id)
        return redirect(url_for('home'))
    return render_template(
        'post.html',
        title='Edit Post',
        username=current_user.username,
        imageSource=IMAGE_SOURCE_URL,
        form=form
    )


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        data = get_form_values(form)
        user = User.query.filter_by(username=data['username'], is_external_user=False).first()
        print(len(user.password_hash))
        print(data['password'])
        if user is None or not user.check_password(data['password']):
            if user is None:
                app.logger.info('Internal account \"%s\" does not existed, login failed', data['username'])
            else:
                app.logger.info('Incorrect password for internal account \"%s\"', user.username)
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        app.logger.info('Internal account \"%s\" were logged in successfully', user.username)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('home')
        return redirect(next_page)
    session["state"] = str(uuid.uuid4())
    auth_url = _build_msal_auth_url(request.url_root[:-1], session["state"])
    return render_template('login.html', title='Sign In', form=form, auth_url=auth_url)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        register_data = get_form_values(form)
        is_user_existed = User.query.filter_by(username=register_data['username'], is_external_user=False).count() > 0
        if is_user_existed:
            form.username.errors.append('Username is already in used')
        else:
            user = User.init_user(register_data['username'], register_data['password'])
            print(len(user.password_hash))
            db.session.add(user)
            db.session.commit()
            flash('Register new account successfully')
            return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route(Config.MS_LOGIN_REDIRECT_PATH)  # Its absolute URL must match your app's redirect_uri set in AAD
def authorized():
    if request.args.get('state') != session.get("state"):
        return redirect(url_for("home"))  # No-OP. Goes back to Index page
    if "error" in request.args:  # Authentication/Authorization failure
        app.logger.warning('Microsoft account login failed, error: %s', request.args.get('error'))
        return render_template("auth_error.html", result=request.args)
    if request.args.get('code'):
        # TODO: Acquire a token from a built msal app, along with the appropriate redirect URI
        msal_app = _build_msal_app()
        result = msal_app.acquire_token_by_authorization_code(
                        request.args.get('code'),
                        Config.SCOPES,
                        f'{request.url_root[:-1]}{Config.MS_LOGIN_REDIRECT_PATH}')
        if "error" in result:
            app.logger.warning('Microsoft account login failed, error: %s', result)
            return render_template("auth_error.html", result=result)
        claims = result.get("id_token_claims")
        session["user"] = claims
        # Note: In a real app, we'd use the 'name' property from session["user"] below
        # Here, we'll use the admin username for anyone who is authenticated by MS
        user = User.init_user(claims["preferred_username"], provider=UserProvider.MICROSOFT)

        user_id = User.query.filter_by(username=user.username, provider=UserProvider.MICROSOFT.value).with_entities(User.id).first()

        if (not user_id):
            db.session.add(user)
            db.session.commit()
        else:
            user.id = user_id[0]
        
        login_user(user)
        app.logger.info('Microsoft account \"%s\" logged in successfully', user.username)
    return redirect(url_for("home"))


@app.route('/logout')
def logout():
    logout_user()
    if session.get("user"): # Used MS Login
        # Wipe out user and its token cache from session
        session.clear()
        # Also logout from your tenant's web session
        return redirect(
            Config.MS_AUTHORITY + "/oauth2/v2.0/logout" +
            "?post_logout_redirect_uri=" + url_for("login", _external=True))

    return redirect(url_for('login'))


def _build_msal_app():
    # TODO: Return a ConfidentialClientApplication
    client_id = Config.MS_CLIENT_ID
    client_secret = Config.MS_CLIENT_SECRET
    authority = Config.MS_AUTHORITY

    return msal.ConfidentialClientApplication(
        client_id,
        client_credential=client_secret,
        authority=authority)


def _build_msal_auth_url(host, state):
    redirect_uri = f'{host}{Config.MS_LOGIN_REDIRECT_PATH}'
    msal_app = _build_msal_app()
    return msal_app.get_authorization_request_url(Config.SCOPES, state=state, redirect_uri=redirect_uri)
