from flask_app import app, db, bcrypt
from flask_app import models
from flask_app.models import User

hashed_pw1 = bcrypt.generate_password_hash('password').decode('utf-8')
librarian = User(username='Librarian', email='admin@bookhub.com', password=hashed_pw1, role='librarian')

app.app_context().push()
    
db.create_all()
db.session.add(librarian)
db.session.commit()

