from CTFd.plugins import register_plugin_assets_directory
from models import Dependencies
from dependencies import (
        plugin_blueprint,
        get_available_challenges,
        satisfies_challenge_dependencies,
        satisfies_hint_dependencies
)

def load(app):
    def _wrap_method(name, wrapper):
        old = app.view_functions[name]
        app.view_functions[name] = satisfies_challenge_dependencies(old)

    app.db.create_all()

    app.view_functions['challenges.chals'] = get_available_challenges
    _wrap_method("challenges.chal_view", satisfies_challenge_dependencies)
    _wrap_method("challenges.chal", satisfies_challenge_dependencies)
    _wrap_method("challenges.hints_view", satisfies_hint_dependencies)

    app.register_blueprint(plugin_blueprint)
    register_plugin_assets_directory(app, base_path='/plugins/ctfd-challenge-dependencies/assets/')
