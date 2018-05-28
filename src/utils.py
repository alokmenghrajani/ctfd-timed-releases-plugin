from flask import abort, session
from CTFd.models import db, Challenges, Solves, Hints
from sqlalchemy import or_, and_
from sqlalchemy.sql import exists
from itertools import groupby
from models import Dependencies

def get_challenges(team_id):
    solves = db.session.query(Solves.chalid).filter(Solves.teamid == team_id)
    db_chals = Challenges.query.filter(or_(Challenges.hidden != True, Challenges.hidden == None),
            and_(~exists().where(
                and_(
                    Dependencies.chalid == Challenges.id, ~Dependencies.dependson.in_(solves)))
            )
    ).order_by(Challenges.value)

    return db_chals.all()


def get_challenges_with_dependencies():
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

def team_can_access_challenge(team_id, chal_id):
    solves = db.session.query(Solves.chalid).filter(Solves.teamid == team_id).all()
    deps = db.session.query(Dependencies.dependson).filter(Dependencies.chalid == chal_id).all()

    return set(deps).issubset(set(solves))

def satisfies_challenge_dependencies(f):
    def wrapper(*args, **kwargs):
        chal_id = kwargs.get("chal_id") or kwargs.get("chalid")
        if chal_id and not team_can_access_challenge(session.get("id", -1), chal_id):
            abort(404)
        return f(*args, **kwargs)
    return wrapper

def satisfies_hint_dependencies(f):
    def wrapper(*args, **kwargs):
        hint_id = kwargs.get("hint_id") or kwargs.get("hintid")
        hint = Hints.query.filter_by(id=hint_id).first_or_404()
        if not team_can_access_challenge(session.get("id", -1), hint.chal):
            abort(404)
        return f(*args, **kwargs)
    return wrapper
