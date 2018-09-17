from flask import abort, session
from CTFd.models import db, Challenges, Solves, Hints
from sqlalchemy import or_, and_
from sqlalchemy.sql import exists
from itertools import groupby
from models import TimedReleases
import datetime
import pdb

def get_challenges():
    now = datetime.datetime.now().replace(microsecond=0)
    db_chals = Challenges.query.filter(or_(Challenges.hidden != True, Challenges.hidden == None)).order_by(Challenges.value).all()

    timed_releases = TimedReleases.query.order_by(TimedReleases.id).all()
    timed_releases_map = { r.chalid: r for r in timed_releases }

    def secondsToText(secs):
        days = int(secs//86400)
        hours = int((secs - days*86400)//3600)
        minutes = int((secs - days*86400 - hours*3600)//60)
        seconds = int(secs - days*86400 - hours*3600 - minutes*60)
        if days > 0:
            return "{0} day{1}, ".format(days, "s" if days!=1 else "") + "{0} hour{1}".format(hours, "s" if hours!=1 else "")
        if hours > 0:
            return "{0} hour{1}, ".format(hours, "s" if hours!=1 else "") + "{0} minute{1}".format(minutes, "s" if minutes!=1 else "")
        if minutes > 0:
            return "{0} minute{1}, ".format(minutes, "s" if minutes!=1 else "") + "{0} second{1}".format(seconds, "s" if seconds!=1 else "")
        return "{0} second{1}".format(seconds, "s" if seconds!=1 else "")

    def time_left(r):
        s = int((r - now).total_seconds())
        return "<span class='countdown' data-time='" + str(s) + "'>" + secondsToText(s) + "</span>"

    challenges = []
    for chal in db_chals:
        if chal.id in timed_releases_map and timed_releases_map[chal.id].release > now:
            chal.name += "<br>" + time_left(timed_releases_map[chal.id].release)
        else:
            chal.name += "<br>&nbsp;"
        challenges += [ chal ];

    return challenges


def get_challenges_with_timed_releases():
    now = datetime.datetime.now().replace(second=0, microsecond=0)
    chals = Challenges.query.order_by(Challenges.id).all()
    chals_map = { c.id: c for c in chals }

    tr = TimedReleases.query.order_by(TimedReleases.id).all()
    tr_map = { r.chalid: r for r in tr }

    def convert(d):
        return d.isoformat()

    challenges = []
    for chal in chals:
        challenges += [{
            "id": chal.id,
            "name": chal.name,
            "timed_release": tr_map[chal.id].release if chal.id in tr_map else None,
            "update_timed_release": convert(tr_map[chal.id].release if chal.id in tr_map else now)
        }]

    return challenges

def can_access_challenge(chal_id):
    tr = db.session.query(TimedReleases).filter(and_(TimedReleases.chalid == chal_id,
        TimedReleases.release > datetime.datetime.now())).count()
    return tr == 0

def satisfies_challenge_timed_releases(f):
    def wrapper(*args, **kwargs):
        chal_id = kwargs.get("chal_id") or kwargs.get("chalid")
        if chal_id and not can_access_challenge(chal_id):
            abort(404)
        return f(*args, **kwargs)
    return wrapper
