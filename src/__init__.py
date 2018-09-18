from CTFd.plugins import register_plugin_assets_directory, register_plugin_script
from models import TimedReleases
from routes import plugin_blueprint, get_available_challenges
from utils import satisfies_challenge_timed_releases

def load(app):
    def wrap_method(name, wrapper):
        old = app.view_functions[name]
        app.view_functions[name] = wrapper(old)

    app.db.create_all()

    # override code which renders challenges to show when future challenges will be released.
    app.view_functions["challenges.chals"] = get_available_challenges

    # override method which render's challenge's data
    wrap_method("challenges.chal_view", satisfies_challenge_timed_releases)

    # disallow attempts to solve future challenges
    wrap_method("challenges.chal", satisfies_challenge_timed_releases)

    app.register_blueprint(plugin_blueprint)
    register_plugin_assets_directory(app, base_path='/plugins/ctfd-timed-releases-plugin/src/assets/')
    register_plugin_script('/plugins/ctfd-timed-releases-plugin/src/assets/countdown.js')
