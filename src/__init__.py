from CTFd.plugins import register_plugin_assets_directory
from models import Dependencies
from dependencies import plugin_blueprint, get_available_challenges

def load(app):
    app.db.create_all()

    app.view_functions['challenges.chals'] = get_available_challenges
    app.register_blueprint(plugin_blueprint)
    register_plugin_assets_directory(app, base_path='/plugins/ctfd-challenge-dependencies/assets/')
