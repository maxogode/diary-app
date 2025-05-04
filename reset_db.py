from app import create_app, db
from app.models import User

app = create_app()

with app.app_context():
    User.query.delete()
    db.session.commit()
    print("All users deleted.")
