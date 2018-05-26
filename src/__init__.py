from models import Dependencies
from dependencies import plugin_blueprint, get_available_challenges

def load(app):
    app.db.create_all()

    app.view_functions['challenges.chals'] = get_available_challenges
    app.register_blueprint(plugin_blueprint)
