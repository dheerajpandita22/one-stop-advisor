import numpy as np
from models import College, Program

# Stream scoring weights (tuneable)
STREAM_WEIGHTS = {
    "Science": {"Math": 0.35, "Science": 0.35, "English": 0.10},
    "Commerce": {"Math": 0.30, "Social Science": 0.25, "English": 0.10},
    "Arts": {"Social Science": 0.35, "English": 0.15},
    "Vocational": {"Science": 0.20, "Math": 0.20, "Social Science": 0.20}
}

# Map RIASEC interests to streams
INTEREST_TO_STREAM = {
    "Realistic": {"Science": 0.25, "Vocational": 0.25},
    "Investigative": {"Science": 0.35},
    "Artistic": {"Arts": 0.40},
    "Social": {"Arts": 0.25, "Commerce": 0.20},
    "Enterprising": {"Commerce": 0.35},
    "Conventional": {"Commerce": 0.30}
}

def normalize_marks(marks):
    by_subject = {}
    for m in marks:
        name = m["subject_name"]
        by_subject[name] = m["obtained"]/max(1,m["max"])
    return by_subject

def score_stream_from_marks(by_subject, stream):
    weights = STREAM_WEIGHTS.get(stream, {})
    if not weights:
        return 0
    score = 0.0
    total_w = sum(weights.values())
    for subj, w in weights.items():
        score += w * by_subject.get(subj, 0.5)  # assume neutral if missing
    return score / total_w if total_w else 0

def score_stream_from_interests(interests, stream):
    s = 0.0
    w = 0.0
    for k, val in interests.items():
        contrib = INTEREST_TO_STREAM.get(k, {}).get(stream, 0)
        s += contrib * val
        w += contrib
    return s / w if w else 0.5

def recommend_streams(interests, marks=None, constraints=None):
    constraints = constraints or {}
    marks_by_subject = normalize_marks(marks) if marks else {}

    streams = ["Science","Commerce","Arts","Vocational"]
    results = []
    for s in streams:
        m_part = score_stream_from_marks(marks_by_subject, s) if marks else 0.5
        i_part = score_stream_from_interests(interests, s) if interests else 0.5
        penalty = 0.0
        budget = constraints.get("budget")
        if budget and s == "Science":
            penalty += 0.05
        score = 0.6*m_part + 0.4*i_part - penalty
        results.append({"stream": s, "score": round(float(score),3),
                        "why": f"Marks fit={round(m_part,2)}, Interests fit={round(i_part,2)}, penalty={round(penalty,2)}"})
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:3]

def recommend_careers(interests, marks, constraints):
    by = normalize_marks(marks)
    top_subjects = sorted(by.items(), key=lambda x: x[1], reverse=True)[:2]
    suggestions = []
    if any(s for s,v in top_subjects if "Math" in s):
        suggestions += ["Engineering","Data Science","Chartered Accountant"]
    if any(s for s,v in top_subjects if "Biology" in s or "Science" in s):
        suggestions += ["Medicine","Pharmacy","Biotech"]
    if any(s for s,v in top_subjects if "English" in s):
        suggestions += ["Law","Mass Communication","Civil Services"]
    if (interests or {}).get("Enterprising",0) > 0.6:
        suggestions += ["Management","Entrepreneurship"]
    if (interests or {}).get("Artistic",0) > 0.6:
        suggestions += ["Design","Fine Arts","Architecture"]

    uniq = []
    for s in suggestions:
        if s not in uniq:
            uniq.append(s)
    return [{"career": c, "reason": "Based on your strong subjects and interest profile."} for c in uniq][:6]

def college_search(q="", state="Jammu & Kashmir", budget=None, program=None):
    query = College.query
    if state:
        query = query.filter(College.state.like(f"%{state}%"))
    if budget:
        try:
            b = int(budget)
            query = query.filter(College.fees_per_year <= b)
        except:
            pass
    cols = query.all()
    out = []
    for c in cols:
        if q and q.lower() not in c.name.lower():
            continue
        if program:
            if not c.programs or int(program) not in c.programs:
                continue
        out.append({
            "id": c.id, "name": c.name, "district": c.district,
            "type": c.type, "fees_per_year": c.fees_per_year,
            "programs": c.programs, "cutoffs": c.cutoffs
        })
    return out[:30]

def advisor_answer(message: str):
    message_l = message.lower()
    sources = []
    answer = "Here’s what I found:\n"
    progs = Program.query.all()
    hits = [p for p in progs if p.name.lower() in message_l]
    if hits:
        p = hits[0]
        answer += f"- Program: {p.name}. Eligibility: {p.eligibility}. Duration: {p.duration_years} years.\n"
        sources.append(f"Program:{p.id}")
    from models import Exam
    exs = Exam.query.all()
    hits_e = [e for e in exs if e.name.lower() in message_l]
    if hits_e:
        e = hits_e[0]
        answer += f"- Exam: {e.name}. Eligibility: {e.eligibility}. Pattern: {e.pattern}.\n"
        sources.append(f"Exam:{e.id}")
    if not hits and not hits_e:
        answer += "- I recommend specifying a program or exam (e.g., “B.Tech cutoff in J&K” or “NEET eligibility”).\n"
    return answer.strip(), sources