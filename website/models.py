from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

# Use One Table
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    work_center = db.Column(db.Float(20))
    username = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    full_name = db.Column(db.String(150))
    employee_num = db.Column(db.Integer)
    
class UserLog(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(150)) 
    full_name = db.Column(db.String(150))
    employee_num = db.Column(db.Integer)
    clock_in_time = db.Column(db.String(40))
    clock_out_time = db.Column(db.String(40))
    hours_clocked = db.Column(db.String(40))
    project_num = db.Column(db.Integer)
    part_num = db.Column(db.Integer)
    hours_allocated = db.Column(db.Float(10))

class MNumber(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    m_num = db.Column(db.Integer)
    

    
    
    
        