from app import db

class Vote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chamber = db.Column(db.String(1))
    vote_num = db.Column(db.Integer, index=True)
    date = db.Column(db.DateTime)
    vote_result = db.Column(db.String(64))
    num_yeas = db.Column(db.Integer)
    num_nays = db.Column(db.Integer)
    num_abstains = db.Column(db.Integer)
    required = db.Column(db.String(10))
    #yeas = db.relationship('Congressperson', backref='yea_vote')
    #nays = db.relationship('Congressperson', backref='nay_vote')
    #not_voting = db.relationship('Congressperson', backref='not_voting')
    question = db.Column(db.String(512))
    #bill = db.relationship('Bill', backref='bill_vote')


    def __repr__(self):
        return '<Vote:{}-{}>'.format(self.chamber, self.vote_num)


