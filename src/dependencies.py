from flask import abort, jsonify, request, Blueprint, session, render_template
from CTFd.models import db, Challenges, Solves, Tags, Hints
from CTFd.plugins.challenges import get_chal_class
from CTFd.plugins import bypass_csrf_protection
from CTFd.utils.decorators import (
    authed_only,
    admins_only,
    during_ctf_time_only,
    require_verified_emails,
    viewable_without_authentication
)
from sqlalchemy import or_, and_
from sqlalchemy.sql import exists
from itertools import groupby
from models import Dependencies

plugin_blueprint = Blueprint("dependencies", __name__, template_folder="../assets")

def _team_can_access_challenge(team_id, chal_id):
    solves = db.session.query(Solves.chalid).filter(Solves.teamid == team_id).all()
    deps = db.session.query(Dependencies.dependson).filter(Dependencies.chalid == chal_id).all()

    return set(deps).issubset(set(solves))

def satisfies_challenge_dependencies(f):
    def wrapper(*args, **kwargs):
        chal_id = kwargs.get("chal_id") or kwargs.get("chalid")
        if chal_id and not _team_can_access_challenge(session.get("id", -1), chal_id):
            abort(404)
        return f(*args, **kwargs)
    return wrapper

def satisfies_hint_dependencies(f):
    def wrapper(*args, **kwargs):
        hint_id = kwargs.get("hint_id") or kwargs.get("hintid")
        hint = Hint.query.filter_by(id=hint_id).first_or_404()
        if not _team_can_access_challenge(session.get("id", -1), hint.chal):
            abort(404)
        return f(*args, **kwargs)
    return wrapper

def _get_challenges_with_dependencies():
    deps = Dependencies.query.order_by(Dependencies.chalid).all()
    deps = { chalid: list(grp) for chalid, grp in groupby(deps, lambda x: x.chalid) }
    chals = Challenges.query.order_by(Challenges.id).all()
    chals_map = { c.id: c for c in chals }
    def get_chal(id):
        return { "id": id, "name": chals_map[id].name }

    challenges = []
    for chal in chals:
        challenges += [{
            "id": chal.id,
            "name": chal.name,
            "dependencies": map(lambda d: get_chal(d.dependson), deps.get(chal.id, []))
        }]

    return challenges

@plugin_blueprint.route("/admin/dependencies", methods=["GET"])
@admins_only
def dependencies():
    challenges = _get_challenges_with_dependencies()
    return render_template("dependencies.html", challenges=challenges)

@plugin_blueprint.route("/admin/dependencies/<int:chal_id>/new", methods=["POST"])
@admins_only
def new_dependency(chal_id):
    chal = Challenges.query.filter_by(id=chal_id).first_or_404()
    dep_chal_id = request.form.get("dependency_id")
    if not dep_chal_id:
        return jsonify({"error": "No dependency id defined!"}), 400
    dep_chal = Challenges.query.filter_by(id=dep_chal_id).first()
    if not dep_chal:
        return jsonify({"error": "No dependency with that id!"}), 400

    db.session.add(Dependencies(chalid=chal.id, dependson=dep_chal.id))
    db.session.commit()
    db.session.close()
    return jsonify({"msg": "ok"})

@plugin_blueprint.route("/admin/dependencies/<int:chal_id>/delete", methods=["POST"])
@admins_only
def delete_dependency(chal_id):
    chal = Challenges.query.filter_by(id=chal_id).first_or_404()
    dep_chal_id = request.form.get("dependency_id")
    print dep_chal_id
    print request.form
    if not dep_chal_id:
        return jsonify({"error": "No dependency id defined!"}), 400
    dep_chal = Challenges.query.filter_by(id=dep_chal_id).first()
    if not dep_chal:
        return jsonify({"error": "No dependency with that id!"}), 400

    deps = Dependencies.query.filter(
            and_(Dependencies.chalid == chal.id, Dependencies.dependson == dep_chal.id)
    ).all()
    for dep in deps:
        db.session.delete(dep)
    db.session.commit()
    db.session.close()
    return jsonify({"msg": "ok"})

def _get_challenges(team_id):
    solves = db.session.query(Solves.chalid).filter(Solves.teamid == team_id)
    db_chals = Challenges.query.filter(or_(Challenges.hidden != True, Challenges.hidden == None),
            and_(~exists().where(
                and_(
                    Dependencies.chalid == Challenges.id, ~Dependencies.dependson.in_(solves)))
            )
    ).order_by(Challenges.value)

    return db_chals.all()

@during_ctf_time_only
@require_verified_emails
@viewable_without_authentication(status_code=403)
def get_available_challenges():
    db_chals = _get_challenges(session.get("id", -1))
    response = {'game': []}
    for chal in db_chals:
        tags = [tag.tag for tag in Tags.query.add_columns('tag').filter_by(chal=chal.id).all()]
        chal_type = get_chal_class(chal.type)
        response['game'].append({
            'id': chal.id,
            'type': chal_type.name,
            'name': chal.name,
            'value': chal.value,
            'category': chal.category,
            'tags': tags,
            'template': chal_type.templates['modal'],
            'script': chal_type.scripts['modal'],
        })

    db.session.close()
    return jsonify(response)
