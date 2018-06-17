from CTFd.plugins import register_plugin_assets_directory
from models import Dependencies
from routes import plugin_blueprint, get_available_challenges
from utils import satisfies_challenge_dependencies, satisfies_hint_dependencies

def load(app):
    def wrap_method(name, wrapper):
        old = app.view_functions[name]
        app.view_functions[name] = wrapper(old)

    app.db.create_all()

    app.view_functions['challenges.chals'] = get_available_challenges
    wrap_method("challenges.chal_view", satisfies_challenge_dependencies)
    wrap_method("challenges.chal", satisfies_challenge_dependencies)
    wrap_method("challenges.hints_view", satisfies_hint_dependencies)

    app.register_blueprint(plugin_blueprint)
    register_plugin_assets_directory(app, base_path='/plugins/ctfd-challenge-dependencies/src/assets/')
