from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Admin, Subject, Chapter, Quiz, Question

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quizmaster.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    user = User.query.get(int(user_id))
    if user:
        return user
    return Admin.query.get(int(user_id))

@app.route('/')
def home():
    return render_template('home.html')

# Admin Dashboard Routes

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    subjects = Subject.query.all()
    users = User.query.all()
    return render_template('admin_dashboard.html', subjects=subjects, users=users)

# CRUD Operations for Subjects
@app.route('/admin/subject/new', methods=['GET', 'POST'])
@login_required
def new_subject():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        subject = Subject(name=name, description=description)
        db.session.add(subject)
        db.session.commit()
        flash('Subject added successfully!')
        return redirect(url_for('admin_dashboard'))
    return render_template('new_subject.html')

@app.route('/admin/subject/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_subject(id):
    subject = Subject.query.get_or_404(id)
    if request.method == 'POST':
        subject.name = request.form['name']
        subject.description = request.form['description']
        db.session.commit()
        flash('Subject updated successfully!')
        return redirect(url_for('admin_dashboard'))
    return render_template('edit_subject.html', subject=subject)

@app.route('/admin/subject/delete/<int:id>', methods=['POST'])
@login_required
def delete_subject(id):
    subject = Subject.query.get_or_404(id)
    db.session.delete(subject)
    db.session.commit()
    flash('Subject deleted successfully!')
    return redirect(url_for('admin_dashboard'))

# Similar routes can be created for Chapters, Quizzes, and Questions.

if __name__ == '__main__':
    app.run(debug=True)