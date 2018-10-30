from flask import jsonify, request, Blueprint, session, render_template
from CTFd.models import db, Challenges, Tags
from CTFd.plugins.challenges import get_chal_class
from CTFd.utils.decorators import (
    admins_only,
    during_ctf_time_only,
    require_verified_emails,
    viewable_without_authentication
)
from sqlalchemy import and_
from models import TimedReleases
from utils import get_challenges, get_challenges_with_timed_releases
import dateutil.parser
import datetime

plugin_blueprint = Blueprint("timed_releases", __name__, template_folder="assets")

@plugin_blueprint.route("/admin/timed_releases", methods=["GET"])
@admins_only
def timed_releases():
    challenges = get_challenges_with_timed_releases()
    return render_template("timed_releases.html", challenges=challenges)

@plugin_blueprint.route("/admin/timed_releases/<int:chal_id>/update", methods=["POST"])
@admins_only
def update_timed_release(chal_id):
    chal = Challenges.query.filter_by(id=chal_id).first_or_404()
    release = request.form.get("release")

    # convert string of the form 2018-06-12T19:30 to a datetime
    release = dateutil.parser.parse(release)

    # update existing timed release or create a new one
    tr = db.session.query(TimedReleases).filter(TimedReleases.chalid == chal_id).first()
    if tr is None:
        # if timed release didn't exist then create it
        db.session.add(TimedReleases(chalid=chal.id, release=release))
    else:
        # if it already existed then update it
        tr.release = release

    db.session.commit()
    db.session.close()
    return jsonify({"msg": "ok"})

@during_ctf_time_only
@require_verified_emails
@viewable_without_authentication(status_code=403)
def get_available_challenges():
    db_chals = get_challenges()
    response = {'game': []}
    for chal in db_chals:
        tags = [tag.tag for tag in Tags.query.add_columns('tag').filter_by(chal=chal["id"]).all()]
        chal_type = get_chal_class(chal["type"])
        response['game'].append({
            'id': chal["id"],
            'type': chal_type.name,
            'name': chal["name"],
            'seconds_before_release': chal["seconds_before_release"],
            'value': chal["value"],
            'category': chal["category"],
            'tags': tags,
            'template': chal_type.templates['modal'],
            'script': chal_type.scripts['modal'],
        })

    db.session.close()
    return jsonify(response)
