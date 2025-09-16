from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import JSON, func
db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    grade_level = db.Column(db.String(10))  # "10", "12", "UG"
    location = db.Column(db.String(120))

class QuizResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    interests_vector = db.Column(JSON)     # dict
    preferences = db.Column(JSON)          # dict
    created_at = db.Column(db.DateTime, server_default=func.now())

class Mark(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    exam_type = db.Column(db.String(10))   # "10","12","UG"
    subject_code = db.Column(db.String(20))
    subject_name = db.Column(db.String(120))
    max_marks = db.Column(db.Integer)
    marks_obtained = db.Column(db.Integer)
    confidence = db.Column(db.Float)

class Recommendation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    type = db.Column(db.String(20))        # "stream","career","college"
    payload = db.Column(JSON)
    rationale = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, server_default=func.now())

class SessionNote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    advisor_type = db.Column(db.String(10))  # "ai","human"
    transcript = db.Column(JSON)
    created_at = db.Column(db.DateTime, server_default=func.now())

class College(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    state = db.Column(db.String(100))
    district = db.Column(db.String(100))
    type = db.Column(db.String(50))        # "Government","Private"
    fees_per_year = db.Column(db.Integer)
    programs = db.Column(JSON)             # list of program ids
    cutoffs = db.Column(JSON)               # dict by program
    placement = db.Column(JSON)             # simple stats

class Program(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    eligibility = db.Column(db.String(400))
    subjects_required = db.Column(JSON)    # list of strings
    duration_years = db.Column(db.Integer)
    level = db.Column(db.String(50))       # "UG","Diploma","Vocational"

class Exam(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    conducting_body = db.Column(db.String(200))
    dates = db.Column(JSON)                # {"application":"", "exam":""}
    eligibility = db.Column(db.String(400))
    pattern = db.Column(db.String(400))

class Scholarship(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    level = db.Column(db.String(50))       # "10","12","UG"
    eligibility = db.Column(db.String(400))
    amount = db.Column(db.Integer)
    state = db.Column(db.String(100))