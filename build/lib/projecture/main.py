import markdown2

from flask import Blueprint, flash, g, redirect
from flask import render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from projecture.db import get_db, get_cursor
from projecture.auth import require_auth
from projecture.project import get_all_projects_by_user_id

main_blueprint = Blueprint('main', __name__)


@main_blueprint.route('/home')
@main_blueprint.route('/')
def index():
    return render_template('main/index.html')


@main_blueprint.route('/about')
def about():
    return render_template('main/about.html')


@main_blueprint.route('/contact')
def contact():
    return render_template('main/contact.html')


@main_blueprint.route('/profile')
@require_auth
def profile():
    projects = get_all_projects_by_user_id(g.user['id'])
    return render_template('main/profile.html', user=g.user, projects=projects, markdown=markdown2)

