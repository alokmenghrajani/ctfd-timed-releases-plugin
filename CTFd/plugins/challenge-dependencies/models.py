from CTFd.models import db

class Dependencies(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chalid = db.Column(db.Integer, db.ForeignKey('challenges.id'))
    dependson = db.Column(db.Integer, db.ForeignKey('challenges.id'))

    def __init__(self, chalid, dependson):
        self.chalid = chalid
        self.dependson = dependson

    def __repr__(self):
        return '<dependency {}, {}>'.format(self.chalid, self.dependson)

