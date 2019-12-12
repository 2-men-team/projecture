import os

from flask import Flask


def create_app(test_config=None):
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_pyfile('config.py', silent=False)

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile(os.path.join('.', 'app/config.py'), silent=True)
    else:
        # load the test config if passed in
        app.config.update(test_config)

    from projecture import db
    db.init_app(app)

    from projecture import auth, project, main
    app.register_blueprint(auth.auth_blueprint)
    app.register_blueprint(project.project_blueprint)
    app.register_blueprint(main.main_blueprint)

    app.add_url_rule('/', endpoint='index')
    # register the database commands
    # from flaskr import db

    # db.init_app(app)

    # apply the blueprints to the app
    # from flaskr import auth, blog

    # app.register_blueprint(auth.auth_blueprint)
    # app.register_blueprint(blog.auth_blueprint)

    # make url_for('index') == url_for('blog.index')
    # in another app, you might define a separate main index here with
    # app.route, while giving the blog blueprint a url_prefix, but for
    # the tutorial the blog will be the main index
    # app.add_url_rule("/", endpoint="index")

    return app
