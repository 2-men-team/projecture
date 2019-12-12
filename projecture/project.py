import markdown2

from flask import Blueprint, flash, g, redirect, current_app
from flask import render_template, request, url_for
from werkzeug.exceptions import abort
from projecture.auth import require_auth
from projecture.db import get_db, get_cursor

project_blueprint = Blueprint('project', __name__, url_prefix='/projects')


def get_all_projects():
    cursor = get_cursor()
    cursor.execute('SELECT * FROM projects')
    return cursor.fetchall()


def get_all_projects_by_user_id(user_id):
    cursor = get_cursor()
    cursor.execute('SELECT * FROM projects WHERE posted_by = %s', (user_id,))
    return cursor.fetchall()


def get_project_by_id(project_id, check_author=False):
    cursor = get_cursor()
    cursor.execute('SELECT * FROM projects WHERE id = %s', (project_id,))
    project = cursor.fetchone()

    if project is None:
        abort(404, 'Project id {0} doesn\'t exist.'.format(project_id))

    if check_author and project['posted_by'] != g.user['id']:
        abort(403)

    return project


def cut_desc(description):
    if description is None:
        return None
    else:
        return description[:current_app.config['BRIEF_DESC_LEN']]


def project_from_request():
    desc = request.form['description']
    return {
        'project_name': request.form['project_name'],
        'posted_by': g.user['id'],
        'link': request.form['link'],
        'complexity': int(request.form['complexity']),
        'brief_description': cut_desc(desc),
        'description': desc
    }


def validate_project(project):
    error = None

    if project['project_name'] is None:
        error = 'Project name is required.'
    elif not project['link']:
        error = 'Link to project repo or chat is required.'
    elif not project['complexity']:
        error = 'Incorrect complexity.'

    return error


def insert_row(table, obj):
    db = get_db()
    cursor = get_cursor()
    pholders = ', '.join(['%s'] * len(obj))
    columns = ', '.join(obj.keys())
    query = 'INSERT INTO %s (%s) VALUES (%s)' % (table, columns, pholders)
    print(query)
    print(obj.values())
    cursor.execute(query, tuple(obj.values()))
    db.commit()


@project_blueprint.route('/index')
@project_blueprint.route('/')
def index():
    projects = get_all_projects()
    return render_template('project/index.html', projects=projects, markdown=markdown2)


@project_blueprint.route('/create', methods=['GET', 'POST'])
@require_auth
def create():
    if request.method == 'POST':
        project = project_from_request()
        error = validate_project(project)

        if error is None:
            insert_row('projects', project)
            return redirect(url_for('project.index'))

        flash(error)

    return render_template('project/create.html')


@project_blueprint.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    project = get_project_by_id(id, check_author=True)

    if request.method == 'POST':
        project = project_from_request()
        error = validate_project(project)

        if error is None:
            cursor = get_cursor()
            cursor.execute('UPDATE projects SET project_name = %s, link = %s, complexity = %s, description = %s'
                           ' WHERE id = %s',
                           (project['project_name'], project['link'], project['complexity'], project['description'], id))
            get_db().commit()
            return redirect(url_for('project.index'))

        flash(error)

    return render_template('project/update.html', project=project)


@project_blueprint.route('/delete/<int:id>')
def delete(id):
    get_project_by_id(id, check_author=True)
    cursor = get_cursor()
    cursor.execute('DELETE FROM projects WHERE id = %s', (id,))
    get_db().commit()
    return redirect(url_for('project.index'))


@project_blueprint.route('/<int:project_id>')
def view(project_id):
    project = get_project_by_id(project_id)
    return render_template('project/project_view.html', project=project, markdown=markdown2)

