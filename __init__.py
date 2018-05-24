from flask import jsonify, request, Blueprint, session
from CTFd.models import db, Challenges, Solves, Tags
from CTFd.plugins.challenges import get_chal_class
from CTFd.challenges import challenges
from CTFd.utils.decorators import (
    authed_only,
    admins_only,
    during_ctf_time_only,
    require_verified_emails,
    viewable_without_authentication
)
from sqlalchemy import or_, and_
from sqlalchemy.sql import exists

class Dependencies(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chalid = db.Column(db.Integer, db.ForeignKey('challenges.id'))
    dependson = db.Column(db.Integer, db.ForeignKey('challenges.id'))

    def __init__(self, chalid, dependson):
        self.chalid = chalid
        self.dependson = dependson

    def __repr__(self):
        return '<dependency {}, {}>'.format(self.chalid, self.dependson)

def load(app):
    app.db.create_all()
    dependencies = Blueprint("dependencies", __name__)

    def get_challenges(team_id):
        solves = app.db.session.query(Solves.chalid).filter(Solves.teamid == team_id)
        db_chals = Challenges.query.filter(or_(Challenges.hidden != True, Challenges.hidden == None),
                and_(~exists().where(
                    and_(
                        Dependencies.chalid == Challenges.id, ~Dependencies.dependson.in_(solves)))
                )
        ).order_by(Challenges.value)

        return db_chals.all()

    @challenges.route("/chals", methods=['GET'])
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

    app.view_functions['challenges.chals'] = get_available_challenges
    app.register_blueprint(dependencies)
