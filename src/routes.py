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
from models import Dependencies
from utils import get_challenges, get_challenges_with_dependencies

plugin_blueprint = Blueprint("dependencies", __name__, template_folder="assets")

@plugin_blueprint.route("/admin/dependencies", methods=["GET"])
@admins_only
def dependencies():
    challenges = get_challenges_with_dependencies()
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

@during_ctf_time_only
@require_verified_emails
@viewable_without_authentication(status_code=403)
def get_available_challenges():
    db_chals = get_challenges(session.get("id", -1))
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
