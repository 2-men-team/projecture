import click

from mysql import connector
from flask import current_app
from flask import g
from flask.cli import with_appcontext


def get_db():
    if 'db' not in g:
        g.db = connector.connect(
            host=current_app.config['DB_HOST'],
            user=current_app.config['DB_USER'],
            passwd=current_app.config['DB_PASS'],
            database=current_app.config['DB_NAME']
        )

    return g.db


def get_cursor():
    if 'cursor' not in g:
        db = get_db()
        g.cursor = db.cursor(dictionary=True)
    return g.cursor


def close_db(e=None):
    cursor = g.pop('cursor', None)
    if cursor is not None:
        cursor.close()

    con = g.pop('db', None)
    if con is not None:
        con.close()


def init_db():
    db = connector.connect(
        host=current_app.config['DB_HOST'],
        user=current_app.config['DB_USER'],
        passwd=current_app.config['DB_PASS']
    )

    cursor = db.cursor()
    with current_app.open_resource(current_app.config['DB_SCHEMA_FILE']) as f:
        cursor.execute(f.read().decode('utf-8'), multi=True)

    cursor.close()


@click.command("init-db")
@with_appcontext
def init_db_command():
    init_db()
    click.echo("Initialized the database.")


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)