import os
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from models import db, User, QuizResult, Mark, Recommendation, SessionNote
from recommender import recommend_streams, recommend_careers, college_search, advisor_answer
from ocr import parse_marksheet
from kb_loader import ensure_kb_loaded

load_dotenv()
app = Flask(__name__, template_folder="../frontend/templates", static_folder="../frontend/static")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///instance/advisor.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret")
CORS(app)
db.init_app(app)

with app.app_context():
    db.create_all()
    ensure_kb_loaded(db)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/quiz")
def quiz():
    return render_template("quiz.html")

@app.route("/marks")
def marks():
    return render_template("marks.html")

@app.route("/advisor")
def advisor():
    return render_template("advisor.html")

@app.route("/colleges")
def colleges_page():
    return render_template("colleges.html")

@app.route("/api/quiz", methods=["POST"])
def api_quiz():
    data = request.json
    user = User(name=data.get("name"), grade_level=data.get("grade"), location=data["profile"].get("location",""))
    db.session.add(user)
    db.session.commit()

    qr = QuizResult(user_id=user.id, interests_vector=data.get("interests", {}), preferences=data.get("profile", {}))
    db.session.add(qr)
    db.session.commit()

    streams = []
    if user.grade_level == "10":
        streams = recommend_streams(interests=data.get("interests", {}), marks=None, constraints=data.get("profile", {}))
    return jsonify({"user_id": user.id, "streams": streams})

@app.route("/api/marks", methods=["POST"])
def api_marks():
    user_id = request.form.get("user_id")
    mode = request.form.get("mode", "manual")

    marks_struct = []
    if mode == "upload" and "file" in request.files:
        marks_struct = parse_marksheet(request.files["file"])
    else:
        import json
        marks_struct = json.loads(request.form.get("marks_json","[]"))

    for m in marks_struct:
        db.session.add(Mark(
            user_id=user_id,
            exam_type=m.get("exam_type","10"),
            subject_code=m.get("subject_code",""),
            subject_name=m.get("subject_name",""),
            max_marks=m.get("max",100),
            marks_obtained=m.get("obtained",0),
            confidence=m.get("confidence",1.0)
        ))
    db.session.commit()

    qr = QuizResult.query.filter_by(user_id=user_id).order_by(QuizResult.created_at.desc()).first()
    interests = qr.interests_vector if qr else {}
    constraints = qr.preferences if qr else {}
    user = User.query.get(user_id)
    marks_for_rec = [{"subject_name": m.subject_name, "obtained": m.marks_obtained, "max": m.max_marks} for m in Mark.query.filter_by(user_id=user_id).all()]

    if user and user.grade_level == "10":
        streams = recommend_streams(interests=interests, marks=marks_for_rec, constraints=constraints)
        rec = Recommendation(user_id=user_id, type="stream", payload={"streams":streams}, rationale="v1 scoring")
        db.session.add(rec); db.session.commit()
        return jsonify({"streams": streams})
    else:
        careers = recommend_careers(interests=interests, marks=marks_for_rec, constraints=constraints)
        rec = Recommendation(user_id=user_id, type="career", payload={"careers":careers}, rationale="v1 scoring")
        db.session.add(rec); db.session.commit()
        return jsonify({"careers": careers})

@app.route("/api/colleges", methods=["GET"])
def api_colleges():
    res = college_search(q=request.args.get("q",""), state=request.args.get("state","Jammu & Kashmir"), budget=request.args.get("budget"), program=request.args.get("program"))
    return jsonify(res)

@app.route("/api/advisor", methods=["POST"])
def api_advisor():
    data = request.json
    answer, sources = advisor_answer(data.get("message",""))
    sn = SessionNote(user_id=data.get("user_id"), advisor_type="ai", transcript=[{"user":data.get("message"),"ai":answer}])
    db.session.add(sn); db.session.commit()
    return jsonify({"answer": answer, "sources": sources})

@app.route("/api/escalate", methods=["POST"])
def api_escalate():
    data = request.json
    sn = SessionNote(user_id=data.get("user_id"), advisor_type="human", transcript=[{"user_note":data.get("note","")}])
    db.session.add(sn); db.session.commit()
    return jsonify({"status":"booked", "message":"A human advisor will contact you soon."})

if __name__ == "__main__":

    app.run(debug=True)
