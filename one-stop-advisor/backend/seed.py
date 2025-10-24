from app import app, db
from kb_loader import ensure_kb_loaded

with app.app_context():
    db.create_all()
    ensure_kb_loaded(db)
    print("DB initialized and KB loaded.")
