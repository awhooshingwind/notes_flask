from flask import(
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from noter.auth import login_required
from noter.db import get_db
import markdown

# md = markdown.Markdown(extensions=['mdx_math'])
extensions = ['mdx_math', 'extra', 'codehilite']
bp = Blueprint('notebook', __name__)

@bp.route('/')
def landing():
    return render_template('landing.html')

@bp.route('/view')
def view():
    if g.user:
        return redirect(url_for('notebook.index'))
    db = get_db()
    db_notes = db.execute(
      'SELECT n.id, title, body, created, author_id, username, isPrivate'
      ' FROM note n JOIN user u ON n.author_id = u.id'
      ' ORDER BY created DESC'  
    ).fetchall()
    notes_pub = []
    for note in db_notes:
        note = dict(note)
        if note['isPrivate'] == 0:
            note['body'] = markdown.markdown(note['body'], extensions=extensions)
            notes_pub.append(note)
    return render_template('view.html', notes=notes_pub)

# add logic for public/private views
@bp.route('/index')
@login_required
def index():
    db = get_db()
    db_notes = db.execute(
      'SELECT n.id, title, body, created, author_id, username, isPrivate'
      ' FROM note n JOIN user u ON n.author_id = u.id'
      ' ORDER BY created DESC'  
    ).fetchall()
    notes = []
    for note in db_notes:
        note = dict(note)
        note['body'] = markdown.markdown(note['body'], extensions=extensions)
        notes.append(note)
    return render_template('notes/index.html', notes=notes)

# testing private index
@bp.route('/private', methods=('GET', 'POST'))
@login_required
def private():
    db = get_db()
    db_notes = db.execute(
      'SELECT *'
      ' FROM note n JOIN user u '
      ' WHERE n.isPrivate = 1 and u.id = n.author_id '
      ' ORDER BY created DESC'  
    ).fetchall()
    priv_notes = []
    for note in db_notes:
        note = dict(note)
        if note['author_id'] == g.user['id']:
            note['body'] = markdown.markdown(note['body'], extensions=extensions)
            priv_notes.append(note)
    return render_template('notes/private.html', notes=priv_notes)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    isPrivate = 0
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        if request.form.get('private'):
            isPrivate = 1
        error = None

        if not title:
            error = 'Needs a title'
        
        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO note (title, body, author_id, isPrivate)'
                ' VALUES (?, ?, ?, ?)',
                (title, body, g.user['id'], isPrivate)
            )
            db.commit()
            return redirect(url_for('notebook.index'))
    
    return render_template('notes/create.html')

def get_note(id, check_author=True):
    note = get_db().execute(
        'SELECT n.id, title, body, created, author_id, username, isPrivate'
        ' FROM note n JOIN user u on n.author_id = u.id'
        ' WHERE n.id = ?',
        (id,)
        ).fetchone()

    if note is None:
        abort(404, f"Note id {id} doesn't exist.")
        
    if check_author and note['author_id'] != g.user['id']:
        abort(403)
        
    return note
    
@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    note = get_note(id)
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        isPrivate = request.form.get('private')
        if(isPrivate):
            isPrivate = 1
        else:
            isPrivate = 0
        error = None

        if not title:
            error = 'Needs a title'
            
        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE note SET title = ?, body = ?, isPrivate = ?'
                ' WHERE id = ?',
                (title, body, isPrivate, id)
                )
            db.commit()
            return redirect(url_for('notebook.index'))
        
    return render_template('notes/update.html', note=note)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_note(id)
    db = get_db()
    db.execute('DELETE FROM note WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('notebook.index'))

@bp.route('/<int:id>/detail', methods=('GET', 'POST',))
@login_required
def detail(id):
    note = get_note(id)
    note = dict(note)
    note['body'] = markdown.markdown(note['body'], extensions=extensions)
    return render_template('notes/detail.html', note=note)