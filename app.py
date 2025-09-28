from flask import Flask
from application.models import db, Admin


app = Flask(__name__)
app.secret_key = "park"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite3'
db.init_app(app)

from application.controllers import *




# ---------------------------------------------------------------------------------------------------------------------------------------------------------
# INITIALIZATION OF DATABSE
# ---------------------------------------------------------------------------------------------------------------------------------------------------------
def initialize_database():
    with app.app_context():
        db.create_all()
        existing_admin = Admin.query.filter(Admin.username=="admin@admin.com").first()
        if not existing_admin:
            default_admin = Admin(name="Admin", username="admin@admin.com", ph_num="1234567890", password="admin1234")
            db.session.add(default_admin)
            db.session.commit()



with app.app_context():
    initialize_database()



# ---------------------------------------------------------------------------------------------------------------------------------------------------------
# RUN APP
# ---------------------------------------------------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
