from CTFd.models import db

class TimedReleases(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chalid = db.Column(db.Integer, db.ForeignKey('challenges.id'))
    release = db.Column(db.DateTime)

    def __init__(self, chalid, release):
        self.chalid = chalid
        self.release = release

    def __repr__(self):
        return '<timed-release {}, {}>'.format(self.chalid, self.release)
