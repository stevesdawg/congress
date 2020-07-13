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
    vote_type = db.Column(db.String(32))
    #yeas = db.relationship('Congressperson', backref='yea_vote')
    #nays = db.relationship('Congressperson', backref='nay_vote')
    #not_voting = db.relationship('Congressperson', backref='not_voting')
    question = db.Column(db.String(512))
    #bill = db.relationship('Bill', backref='bill_vote')

    def __repr__(self):
        return '<Vote:{}-{}>'.format(self.chamber, self.vote_num)


class DeficitSurplus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer, index=True)
    total_receipt = db.Column(db.Integer)
    total_outlay = db.Column(db.Integer)
    total_net = db.Column(db.Integer)
    onbud_receipt = db.Column(db.Integer)
    onbud_outlay = db.Column(db.Integer)
    onbud_net = db.Column(db.Integer)
    offbud_receipt = db.Column(db.Integer)
    offbud_outlay = db.Column(db.Integer)
    offbud_net = db.Column(db.Integer)

    def __repr__(self):
        return '<DefSur:{}-{}>'.format(self.year, self.total_net)


class ReceiptBreakdown(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer, index=True)
    indiv_income_tax = db.Column(db.Integer)
    corp_income_tax = db.Column(db.Integer)
    soc_ins_retire_total = db.Column(db.Integer)
    excise_tax = db.Column(db.Integer)
    other = db.Column(db.Integer)

    def __repr__(self):
        return '<Receipt:{}-{}>'.format(self.year, self.indiv_income_tax)


class OutlayBreakdown(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer, index=True)
    nat_def = db.Column(db.Integer)
    nat_def_perc_outlays = db.Column(db.Float)
    nat_def_perc_gdp = db.Column(db.Float)

    hum_res = db.Column(db.Integer)
    hum_res_perc_outlays = db.Column(db.Float)
    hum_res_perc_gdp = db.Column(db.Float)
    edu = db.Column(db.Integer)
    health = db.Column(db.Integer)
    medicare = db.Column(db.Integer)
    income_secur = db.Column(db.Integer)
    social_secur = db.Column(db.Integer)
    vet_benef = db.Column(db.Integer)

    phys_res = db.Column(db.Integer)
    phys_res_perc_outlays = db.Column(db.Float)
    phys_res_perc_gdp = db.Column(db.Float)
    energy = db.Column(db.Integer)
    nat_res_env = db.Column(db.Integer)
    commerce_house = db.Column(db.Integer)
    transport = db.Column(db.Integer)
    comm_reg_dev = db.Column(db.Integer)

    net_interest = db.Column(db.Integer)
    net_interest_perc_outlays = db.Column(db.Float)
    net_interest_perc_gdp = db.Column(db.Float)

    other_funcs = db.Column(db.Integer)
    other_funcs_perc_outlays = db.Column(db.Float)
    other_funcs_perc_gdp = db.Column(db.Float)
    intl_aff = db.Column(db.Integer)
    sci_spa_tech = db.Column(db.Integer)
    agriculture = db.Column(db.Integer)
    admin_justice = db.Column(db.Integer)
    gen_gov = db.Column(db.Integer)
