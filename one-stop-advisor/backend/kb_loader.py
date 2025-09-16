import os, csv
from models import db, College, Program, Exam, Scholarship

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

def ensure_kb_loaded(db_session):
    # Load once if empty
    if Program.query.first():
        return
    # Programs
    with open(os.path.join(DATA_DIR, "programs.csv"), encoding="utf-8") as f:
        for i, row in enumerate(csv.DictReader(f)):
            db.session.add(Program(
                id=i+1,
                name=row["name"],
                eligibility=row["eligibility"],
                subjects_required=row["subjects_required"].split("|"),
                duration_years=int(row["duration_years"]),
                level=row["level"]
            ))
    # Colleges
    with open(os.path.join(DATA_DIR, "colleges.csv"), encoding="utf-8") as f:
        for i, row in enumerate(csv.DictReader(f)):
            progs = [int(x) for x in row["programs"].split("|") if x]
            db.session.add(College(
                id=i+1,
                name=row["name"],
                state=row["state"],
                district=row["district"],
                type=row["type"],
                fees_per_year=int(row["fees_per_year"]),
                programs=progs,
                cutoffs={"B.Tech": row.get("cutoff_btech","")},
                placement={"median_lpa": row.get("median_lpa","")}
            ))
    # Exams
    with open(os.path.join(DATA_DIR, "exams.csv"), encoding="utf-8") as f:
        for i, row in enumerate(csv.DictReader(f)):
            db.session.add(Exam(
                id=i+1,
                name=row["name"],
                conducting_body=row["conducting_body"],
                dates={"application": row["application_date"], "exam": row["exam_date"]},
                eligibility=row["eligibility"],
                pattern=row["pattern"]
            ))
    # Scholarships
    with open(os.path.join(DATA_DIR, "scholarships.csv"), encoding="utf-8") as f:
        for i, row in enumerate(csv.DictReader(f)):
            db.session.add(Scholarship(
                id=i+1,
                name=row["name"],
                level=row["level"],
                eligibility=row["eligibility"],
                amount=int(row["amount"]),
                state=row["state"]
            ))
    db.session.commit()