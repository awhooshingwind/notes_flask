import functools

from flask import(
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from itsdangerous import NoneAlgorithm
from werkzeug.security import check_password_hash, generate_password_hash

from noter.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = 'We need to call you something...pick a username'
        elif not password:
            error = 'You need a password to get back in'
        
        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (username, password) VALUES (?, ?)",
                    (username, generate_password_hash(password)),
                )
                db.commit()
            except db.IntegrityError:
                error = f"User {username} already exists."
            else:
                user = db.execute(
                    'SELECT * FROM user WHERE username = ?', (username,)
                    ).fetchone()
                session['userID'] = user['userID']
                return redirect(url_for("notebook.index"))
        
        flash(error)
    
    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Nobody called that around here...'
        elif not check_password_hash(user['password'], password):
            error = 'Wrong password'
        
        if error is None:
            session.clear()
            session['userID'] = user['userID']
            return redirect(url_for('notebook.index'))
        
        flash(error)
    
    return render_template('auth/login.html')

@bp.before_app_request
def load_logged_in_user():
    userID = session.get('userID')

    if userID is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE userID = ?', (userID,)
        ).fetchone()

@bp.route('logout')
def logout():
    session.clear()
    return redirect(url_for('notebook.landing'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        
        return view(**kwargs)
    
    return wrapped_view