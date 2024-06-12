from datetime import datetime, timedelta
from flask_app import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

user_books = db.Table('user_books',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('book_id', db.Integer, db.ForeignKey('book.id')),
    db.Column('date_issued', db.DateTime, nullable=False, default=datetime.utcnow),
    db.Column('return_date', db.DateTime, nullable=False)
)

completed_books = db.Table('completed_books',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('book_id', db.Integer, db.ForeignKey('book.id')),
    db.Column('date_completed', db.DateTime, nullable=False, default=datetime.utcnow),
)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')
    profile_pic = db.Column(db.String(100), nullable=True, default='static/profile_pics/default.png')

    book_requests = db.relationship('BookRequest', backref='requested_by', lazy=True)
    issued_books = db.relationship('Book', secondary=user_books, backref='issued_to_users', lazy=True)
    completed_books = db.relationship('Book', secondary=completed_books, backref='completed_by_users', lazy=True)

    def __repr__(self):
        return f"User(id={self.id}, username='{self.username}', email='{self.email}', role='{self.role}')"

class Section(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    description = db.Column(db.Text)

    books = db.relationship('Book', backref='section', lazy=True)

    def __repr__(self):
        return f"Section(id={self.id}, name='{self.name}', date_created='{self.date_created}', description='{self.description}')"

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    pdf = db.Column(db.String(255), nullable=False) 
    authors = db.Column(db.String(200), nullable=False)
    section_id = db.Column(db.Integer, db.ForeignKey('section.id'), nullable=False)
    book_requests = db.relationship('BookRequest', backref='book', lazy=True)
    
    def __repr__(self):
        return f"Book(id={self.id}, name='{self.name}', pdf='{self.pdf}', authors='{self.authors}')"

class BookRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    days_requested = db.Column(db.Integer, nullable=False)
    request_status = db.Column(db.String(20), nullable=False, default='pending')
    date_requested = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    return_date = db.Column(db.DateTime, nullable=False)

    def __init__(self, book_id, user_id, days_requested):
        self.book_id = book_id
        self.user_id = user_id
        self.days_requested = days_requested
        self.return_date = datetime.utcnow() + timedelta(days=days_requested)

    def __repr__(self):
        return f"BookRequest(id={self.id}, book_id={self.book_id}, user_id={self.user_id}, request_status='{self.request_status}', date_requested='{self.date_requested}', return_date='{self.return_date}')"

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id', ondelete='CASCADE'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    review = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    user = db.relationship('User', backref='reviews')
    book = db.relationship('Book', backref='reviews')

    def __repr__(self):
        return f"Review(id={self.id}, user_id={self.user_id}, book_id={self.book_id}, rating={self.rating}, review_text='{self.review_text}', date_posted='{self.date_posted}')"
