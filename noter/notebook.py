from flask import(
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from noter.auth import login_required
from noter.db import get_db
from noter.logic import *
from datetime import datetime, timedelta, date

bp = Blueprint('notebook', __name__)

@bp.route('/')
def landing():
    fun = np.random.randint(5000)
    return render_template('landing.html', fun=fun)

@bp.route('/view')
def view():
    db = get_db()
    db_notes = db.execute(
      'SELECT *'
      ' FROM note n JOIN user u '
      ' WHERE n.isPrivate = 0 and u.userID = n.authorID '
      ' ORDER BY created DESC'  
    ).fetchall()
    db_tasks = db.execute(
        'SELECT *'
        ' FROM task t JOIN user u'
        ' WHERE t.isPrivate = 0 and u.userID = t.authorID '
        ' ORDER BY dueDate'
    ).fetchall()
    pub_tasks = []
    for task in db_tasks:
        task = dict(task)
        task['todo'] = make_md(task['todo'])
        pub_tasks.append(task)
    pub_notes = []
    for note in db_notes:
        note = dict(note)
        note['body'] = make_md(note['body'])
        pub_notes.append(note)
    return render_template('view_template.html', notes=pub_notes, tasks=pub_tasks)


@bp.route('/index')
@login_required
def index():
    db = get_db()
    db_notes = db.execute(
      'SELECT n.noteID, title, body, created, authorID, username, isPrivate'
      ' FROM note n JOIN user u ON n.authorID = u.userID'
      ' ORDER BY created DESC'  
    ).fetchall()
    notes = []
    for note in db_notes:
        note = dict(note)
        note['body'] = make_md(note['body'])
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
      ' WHERE n.isPrivate = 1 and u.userID = n.authorID '
      ' ORDER BY created DESC'  
    ).fetchall()
    db_tasks = db.execute(
        'SELECT *'
        ' FROM task t JOIN user u'
        ' WHERE t.isPrivate = 1 and u.userID = t.authorID '
        ' ORDER BY dueDate'
    ).fetchall()
    priv_tasks = []
    for task in db_tasks:
        task = dict(task)
        if task['authorID'] == g.user['userID']:
            task['todo'] = make_md(task['todo'])
            priv_tasks.append(task)
    priv_notes = []
    for note in db_notes:
        note = dict(note)
        if note['authorID'] == g.user['userID']:
            note['body'] = make_md(note['body'])
            priv_notes.append(note)
    return render_template('notes/private.html', notes=priv_notes, tasks=priv_tasks)


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
                'INSERT INTO note (title, body, authorID, isPrivate)'
                ' VALUES (?, ?, ?, ?)',
                (title, body, g.user['userID'], isPrivate)
            )
            db.commit()
            return redirect(url_for('notebook.index'))
    
    return render_template('notes/create.html')

def get_note(noteID, check_author=True):
    note = get_db().execute(
        'SELECT n.noteID, title, body, created, authorID, username, isPrivate'
        ' FROM note n JOIN user u on n.authorID = u.userID'
        ' WHERE n.noteID = ?',
        (noteID,)
        ).fetchone()

    if note is None:
        abort(404, f"Note ID {noteID} doesn't exist.")
        
    if check_author and note['authorID'] != g.user['userID']:
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
                ' WHERE noteID = ?',
                (title, body, isPrivate, id)
                )
            db.commit()
            return redirect(url_for('notebook.index'))
        
    return render_template('notes/update.html', note=note, item='note')

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
    note['body'] = make_md(note['body'])
    if note['isPrivate']:
        return render_template('notes/detail.html', note=note)
    return

# Testing Tasks Code
@bp.route('/task', methods=('GET', 'POST'))
@login_required
def make_task():
    isPrivate = 1
    if request.method == 'POST':
        todo = request.form['todo']
        dueDate = request.form['due']
        if not request.form.get('private'):
            isPrivate = 0
        error = None

        if not todo:
            error = 'To do nothing and be content, if only...'
        
        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO task (todo, authorID, dueDate, isPrivate)'
                ' VALUES (?, ?, ?, ?)',
                (todo, g.user['userID'], dueDate, isPrivate)
            )
            db.commit()
            return redirect(url_for('notebook.tasking'))
    
    return render_template('make.html', item='task')

def get_task(id, check_author=True):
    task = get_db().execute(
        'SELECT *'
        ' FROM task t JOIN user u on t.authorID = u.userID'
        ' WHERE t.taskID = ?',
        (id,)
        ).fetchone()

    if task is None:
        abort(404, f"Note id {id} doesn't exist.")
        
    if check_author and task['authorID'] != g.user['userID']:
        abort(403)
        
    return task

@bp.route('/<int:id>/taskupdate', methods=('GET', 'POST'))
@login_required
def task_update(id):
    task = get_task(id)
    if request.method == 'POST':
        todo = request.form['todo']
        dueDate = request.form['due']
        isPrivate = request.form.get('private')
        if(isPrivate):
            isPrivate = 1
        else:
            isPrivate = 0
        error = None

        if not todo:
            error = 'Nothing from nothing leaves...well you know..'
            
        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE task SET todo = ?, dueDate = ?, isPrivate = ?'
                ' WHERE taskID = ?',
                (todo, dueDate, isPrivate, id)
                )
            db.commit()
            return redirect(url_for('notebook.tasking'))
        
    return render_template('notes/better_update.html', task=task, item=['task'])

@bp.route('/tasking')
@login_required
def tasking():
    now = date.today()
    db = get_db()
    db_tasks = db.execute(
      'SELECT *'
      ' FROM task t JOIN user u ON t.authorID = u.userID'
      ' ORDER BY dueDate'  
    ).fetchall()
    tasks = []
    soon = timedelta(days=3)
    for task in db_tasks:
        task = dict(task)
        task['todo'] = make_md(task['todo'])
        tasks.append(task)
    return render_template('notes/taskview.html', tasks=tasks, now=now, soon=soon)