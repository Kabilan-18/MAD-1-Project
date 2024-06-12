from flask_app import app, db, bcrypt
from flask import render_template, url_for, flash, redirect, request
from flask_app.forms import RegistrationForm, LoginForm, SectionForm, BookForm
from flask_login import login_user, current_user, logout_user, login_required
from flask_app.models import User, Section, Book, BookRequest, Feedback, user_books, completed_books
from datetime import datetime, timedelta
from sqlalchemy import insert
import os
import matplotlib.pyplot as plt
import seaborn as sns
import secrets

@app.route('/')
def home():
    books = Book.query.all()
    sections = Section.query.all()
    if not books:
        return render_template('empty.html', title='Home')
    return render_template('index.html', title='Home', books=books, sections=sections)

@app.route('/search', methods=['POST'])
def search():
    search_category = request.form['search_category']
    search_query = request.form['search_query']
    books, sections = [], []
    if search_category == 'book':
        books = Book.query.filter(Book.name.like(f'%{search_query}%')).all()
    elif search_category == 'section':
        sections = Section.query.filter(Section.name.like(f'%{search_query}%')).all()
    else:
        books = Book.query.filter(Book.authors.like(f'%{search_query}%')).all()
    return render_template('search.html', title='Search Results', books=books, sections=sections, search_query=search_query, search_category=search_category)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data) and user.role=='user':
            login_user(user, remember=form.remember.data)
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route('/librarian-login', methods=['GET', 'POST'])
def librarian_login():
    form = LoginForm()
    if form.validate_on_submit():
        librarian = User.query.filter_by(email=form.email.data, role='librarian').first()
        if librarian and bcrypt.check_password_hash(librarian.password, form.password.data) and librarian.role=='librarian':
            login_user(librarian, remember=form.remember.data)
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password', 'danger')
            return redirect(url_for('home'))
    return render_template('librarian_login.html', title='Librarian Login', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/sections')
@login_required
def sections():
    form = SectionForm()
    existing_sections = Section.query.all()
    return render_template('sections.html', title='Manage Sections', sections=existing_sections, form=form)

@app.route('/add-section', methods=['GET', 'POST'])
@login_required
def add_section():
    form = SectionForm()
    if form.validate_on_submit():
        section = Section(name=form.name.data, description=form.description.data)
        db.session.add(section)
        db.session.commit()
        flash('Section added successfully!', 'success')
        return redirect(url_for('sections'))
    
@app.route('/update-section/<int:section_id>', methods=['POST'])
@login_required
def update_section(section_id):
    section = Section.query.get_or_404(section_id)
    section.name = request.form['name']
    section.description = request.form['description']
    db.session.commit()
    flash('Section updated successfully!', 'success')
    return redirect(url_for('sections'))

@app.route('/delete-section/<int:section_id>', methods=['POST'])
@login_required
def delete_section(section_id):
    section = Section.query.get_or_404(section_id)
    section_books = Book.query.filter_by(section_id=section_id).all()
    for book in section_books:
        db.session.delete(book)
    db.session.delete(section)
    db.session.commit()
    flash('Section deleted successfully!', 'success')
    return redirect(url_for('sections'))

@app.route('/books')
@login_required
def books():
    form = BookForm()
    existing_sections = Section.query.all()
    existing_books = Book.query.all()
    return render_template('books.html', title='Manage Books', books=existing_books, sections=existing_sections, form=form)

    
def save_pdf(form_pdf):
    random_hex = secrets.token_hex(16)
    _, f_ext = os.path.splitext(form_pdf.filename)
    pdf_filename = random_hex + f_ext
    pdf_directory = os.path.join(app.root_path, 'static', 'books')

    if not os.path.exists(pdf_directory):
        os.makedirs(pdf_directory)

    pdf_path = os.path.join(pdf_directory, pdf_filename)

    form_pdf.save(pdf_path)

    return pdf_filename

def delete_pdf(pdf_filename):
    pdf_directory = os.path.join(app.root_path, 'static', 'books')
    pdf_path = os.path.join(pdf_directory, pdf_filename)

    if os.path.exists(pdf_path):
        os.remove(pdf_path)
        return True
    else:
        return False

@app.route('/book/<int:book_id>', methods=['GET'])
@login_required
def display_book(book_id):
    book = Book.query.get_or_404(book_id)
    pdf_path = url_for('static', filename='books/' + book.pdf)
    return render_template('display_book.html', pdf_path=pdf_path)

@app.route('/add-book', methods=['GET', 'POST'])
@login_required
def add_book():
    form = BookForm()
    if form.validate_on_submit():
        pdf_filename = save_pdf(form.pdf.data)
        book = Book(name=form.name.data, pdf=pdf_filename, authors=form.authors.data, section_id=form.section.data)
        db.session.add(book)
        db.session.commit()
        flash('Book added successfully!', 'success')
        return redirect(url_for('books'))
    books = Book.query.all()
    sections = Section.query.all()
    return render_template('books.html', form=form, books=books, sections=sections)

@app.route('/update-book/<int:book_id>', methods=['POST'])
@login_required
def update_book(book_id):
    book = Book.query.get_or_404(book_id)
    book.name = request.form['name']
    book.authors = request.form['authors']
    book.section_id = request.form['section']
    db.session.commit()
    flash('Book updated successfully!', 'success')
    return redirect(url_for('books'))

@app.route('/delete-book/<int:book_id>', methods=['POST'])
@login_required
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    delete_pdf(book.pdf)
    db.session.delete(book)
    db.session.commit()
    flash('Book deleted successfully!', 'success')
    return redirect(url_for('books'))

@app.route('/my-books')
@login_required
def my_books():
    user = User.query.get(current_user.id)
    pending_requests = user.book_requests
    issued_books = user.issued_books
    completed_books = user.completed_books
    return render_template('my_books.html', title='My Books' ,pending_requests=pending_requests, issued_books=issued_books, completed_books=completed_books)


@app.route('/request/<int:book_id>', methods=['POST'])
@login_required
def request_book(book_id):
    if len(current_user.issued_books) >= 5:
        flash('You have been already issued 5 books. Please return some books.', 'danger')
        return redirect(url_for('my_books'))
    else:
        days = int(request.form["days"])
        book_request = BookRequest(book_id=book_id, user_id=current_user.id, days_requested=days)
        db.session.add(book_request)
        db.session.commit()
        return redirect(url_for('home')) 

@app.route('/issues', methods=['GET'])
@login_required
def issues():
    book_requests = BookRequest.query.all()
    return render_template('issues.html', title='Issues', book_requests=book_requests)

@app.route('/cancel-request/<int:book_request_id>', methods=['GET'])
@login_required
def cancel_request(book_request_id):
    request = BookRequest.query.get_or_404(book_request_id)
    db.session.delete(request)
    db.session.commit()
    flash('Request cancelled successfully!', 'success')
    return redirect(url_for('my_books'))

@app.route('/reject-request/<int:book_request_id>', methods=['GET'])
@login_required
def reject_request(book_request_id):
    request = BookRequest.query.get_or_404(book_request_id)
    db.session.delete(request)
    db.session.commit()
    flash('Request rejected successfully!', 'success')
    return redirect(url_for('issues'))

@app.route('/issue-book/<int:book_request_id>', methods=['GET'])
@login_required
def issue_book(book_request_id):
    request = BookRequest.query.get_or_404(book_request_id)
    return_date = datetime.utcnow() + timedelta(days=request.days_requested)
    request.return_date = return_date
    request.request_status = 'issued'
    association = {
        'user_id': request.requested_by.id,
        'book_id': request.book.id,
        'date_issued': datetime.utcnow(),
        'return_date': return_date
    }
    db.session.execute(insert(user_books).values(association))
    db.session.commit()
    flash('Book issued successfully!', 'success')
    return redirect(url_for('issues'))

@app.route('/revoke-book/<int:book_request_id>', methods=['GET'])
@login_required
def revoke_book(book_request_id):
    request = BookRequest.query.get_or_404(book_request_id)
    user = User.query.get(request.requested_by.id)
    book = Book.query.get(request.book.id)
    user.issued_books.remove(book)
    db.session.delete(request)
    db.session.commit()
    flash('Book revoked successfully!', 'success')
    return redirect(url_for('issues'))

@app.route('/return-book/<int:book_id>', methods=['POST'])
@login_required
def return_book(book_id):
    user = User.query.get(current_user.id)
    book = Book.query.get(book_id)
    book_request = BookRequest.query.filter_by(book_id=book_id, user_id=user.id).first()
    feedback = Feedback(book_id=book_id, user_id=current_user.id, rating=request.form['rating'], review=request.form['review'])
    user.issued_books.remove(book)
    user.completed_books.append(book)
    db.session.delete(book_request)
    db.session.add(feedback)
    db.session.commit()
    flash('Book returned successfully!', 'success')
    return redirect(url_for('my_books'))

def generate_admin_pie_chart(sections):
    section_book_counts = {section.name: len(section.books) for section in sections if section.books}
    sns.set_theme(style='whitegrid')
    plt.figure(figsize=(10, 7))
    plt.pie(section_book_counts.values(), labels=section_book_counts.keys(), autopct='%.2f%%', startangle=120, colors=sns.color_palette('muted'))
    plt.tight_layout()
    pie_chart_path = os.path.join(app.root_path, 'static', 'charts', 'admin_pie_chart.png')
    plt.savefig(pie_chart_path)
    plt.close()
    return pie_chart_path

def generate_admin_bar_chart(pending_count, issued_count, completed_count):
    sns.set_theme(style='whitegrid')
    plt.figure(figsize=(10, 7))
    plt.bar(['Pending', 'Issued', 'Completed'], [pending_count, issued_count, completed_count], color=sns.color_palette('muted'))
    plt.tight_layout()
    bar_chart_path = os.path.join(app.root_path, 'static', 'charts', 'admin_bar_chart.png')
    plt.savefig(bar_chart_path)
    plt.close()
    return bar_chart_path

@app.route('/admin-dashboard')
@login_required
def admin_dashboard():
    total_users = User.query.count()
    total_books = Book.query.count()
    total_sections = Section.query.count()

    sections = Section.query.all()
    generate_admin_pie_chart(sections)

    pending_count = BookRequest.query.filter_by(request_status='pending').count()
    issued_count = BookRequest.query.filter_by(request_status='issued').count()
    completed_count = db.session.query(completed_books).count()
    generate_admin_bar_chart(pending_count, issued_count, completed_count)

    return render_template('admin_dashboard.html', title='Dashboard' , total_users=total_users, total_books=total_books, total_sections=total_sections)

def generate_user_pie_chart(completed_books):
    section_book_counts = {book.section.name: len(book.section.books) for book in completed_books}
    sns.set_theme(style='whitegrid')
    plt.figure(figsize=(10, 7))
    plt.pie(section_book_counts.values(), labels=section_book_counts.keys(), autopct='%.2f%%', startangle=120, colors=sns.color_palette('muted'))
    plt.tight_layout()
    pie_chart_path = os.path.join(app.root_path, 'static', 'charts', 'user_pie_chart.png')
    plt.savefig(pie_chart_path)
    plt.close()
    return pie_chart_path    

def generate_user_bar_chart(pending_count, issued_count, completed_count):
    sns.set_theme(style='whitegrid')
    plt.figure(figsize=(10, 7))
    plt.bar(['Pending', 'Issued', 'Completed'], [pending_count, issued_count, completed_count], color=sns.color_palette('muted'))
    plt.tight_layout()
    bar_chart_path = os.path.join(app.root_path, 'static', 'charts', 'user_bar_chart.png')
    plt.savefig(bar_chart_path)
    plt.close()
    return bar_chart_path

@app.route('/user-dashboard')
@login_required
def user_dashboard():
    pending_count = BookRequest.query.filter_by(user_id=current_user.id, request_status='pending').count()
    issued_count = len(current_user.issued_books)
    completed_books = current_user.completed_books
    completed_count = len(completed_books)
    generate_user_pie_chart(completed_books)
    generate_user_bar_chart(pending_count, issued_count, completed_count)
    return render_template('user_dashboard.html', title='Dashboard')

@app.route('/change_password', methods=['POST'])
def change_password():
    if request.method == 'POST':
        if request.form['new_password'] == request.form['confirm_password']:
            new_password = request.form['new_password']
            new_password_hashed = bcrypt.generate_password_hash(new_password).decode('utf-8')
            current_user.password = new_password_hashed
            db.session.commit()
            flash('Password changed successfully!', 'success')
            return redirect(url_for('account')) 
        else:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('account'))

@app.route('/account')
def account():
    return render_template('account.html', title='Account')

@app.route('/about')
def about():
    return render_template('about.html', title='About')
