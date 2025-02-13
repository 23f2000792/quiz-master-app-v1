import os
from flask import Flask, render_template, request, redirect, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Get the current directory
curr_dir = os.path.dirname(os.path.abspath(__file__))

# Creating a Flask instance
app = Flask(__name__, template_folder="templates")

app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiz_master.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy()

# Bind SQLAlchemy to the app
db.init_app(app)


# User Model
class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    full_name = db.Column(db.String(200), nullable=False)
    qualification = db.Column(db.String(100))
    dob = db.Column(db.Date, nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    scores = db.relationship('Score', back_populates='user')
    quizzes_created = db.relationship('Quiz', backref='creator', lazy=True)


# Other Models (Subject, Chapter, Quiz, Question, Score) remain unchanged
class Subject(db.Model):
    __tablename__ = 'subject'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    chapters = db.relationship('Chapter', backref='subject', lazy=True)


class Chapter(db.Model):
    __tablename__ = 'chapter'
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'))
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    quizzes = db.relationship('Quiz', backref='chapter', lazy=True)


class Quiz(db.Model):
    __tablename__ = 'quiz'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id'))
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    date_of_quiz = db.Column(db.Date, nullable=False)
    time_duration = db.Column(db.Integer, nullable=False)
    remarks = db.Column(db.Text)
    questions = db.relationship('Question', backref='quiz', lazy=True)
    scores = db.relationship('Score', backref='quiz', lazy=True)


class Question(db.Model):
    __tablename__ = 'question'
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'))
    question_statement = db.Column(db.Text, nullable=False)
    options = db.Column(db.Text, nullable=False)
    correct_option = db.Column(db.String(50), nullable=False)


class Score(db.Model):
    __tablename__ = 'score'
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    time_stamp_of_attempt = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    total_score = db.Column(db.Integer, nullable=False)
    user = db.relationship('User', back_populates='scores')


# Routes
@app.route('/')
def home():
    return render_template('home.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        full_name = request.form.get('full_name')
        dob_str = request.form.get('dob')
        qualification = request.form.get('qualification')

        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return redirect('/register')

        new_user = User(
            username=username,
            password=password,
            full_name=full_name,
            dob=datetime.strptime(dob_str, '%Y-%m-%d'),
            qualification=qualification
        )
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please log in.', 'success')
        return redirect('/login')

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and user.password == password:
            session['user_id'] = user.id
            session['is_admin'] = user.is_admin
            flash('Login successful!', 'success')
            return redirect('/admin_dashboard' if user.is_admin else '/user_dashboard')
        else:
            flash('Invalid username or password', 'danger')

    return render_template('login.html')


@app.route('/admin_dashboard')
def admin_dashboard():
    if 'user_id' not in session or not session.get('is_admin'):
        flash('Unauthorized access.', 'danger')
        return redirect('/login')

    subjects = Subject.query.all() 
    return render_template('admin_dashboard.html', subjects=subjects)


@app.route('/user_dashboard')
def user_dashboard():
    if 'user_id' not in session:
        flash('You must be logged in to view this page.', 'danger')
        return redirect('/login')

    quizzes_available = Quiz.query.all()
    return render_template('user_dashboard.html', quizzes=quizzes_available)


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect('/')

# Admin Routes
@app.route('/create_subject', methods=['GET', 'POST'])
def create_subject():
    if 'user_id' not in session or not session.get('is_admin'):
        flash('Unauthorized access.', 'danger')
        return redirect('/login')

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']

        new_subject = Subject(name=name, description=description)
        db.session.add(new_subject)
        db.session.commit()
        flash('Subject created successfully!', 'success')
        return redirect('/admin_dashboard')

    return render_template('create_subject.html')

@app.route('/create_chapter', methods=['GET', 'POST'])
def create_chapter():
    if 'user_id' not in session or not session.get('is_admin'):
        flash('Unauthorized access.', 'danger')
        return redirect('/login')

    subjects = Subject.query.all()

    if request.method == 'POST':
        subject_id = request.form['subject_id'] 
        name = request.form['name']
        description = request.form['description']

        new_chapter = Chapter(subject_id=subject_id, name=name, description=description)
        db.session.add(new_chapter)
        db.session.commit()
        flash('Chapter created successfully!', 'success')
        return redirect('/admin_dashboard')

    return render_template('create_chapter.html', subjects=subjects)


@app.route('/create_question', methods=['GET', 'POST'])
def create_question():
    if 'user_id' not in session or not session.get('is_admin'):
        flash('Unauthorized access.', 'danger')
        return redirect('/login')

    quiz_id = request.args.get('quiz_id')

    if not quiz_id:
        flash('Invalid quiz selection! Quiz ID is missing.', 'danger')
        return redirect('/quiz_management')

    try:
        quiz_id = int(quiz_id) 
    except ValueError:
        flash('Invalid quiz ID! Must be a number.', 'danger')
        return redirect('/quiz_management')

    quiz = Quiz.query.get(quiz_id)
    if not quiz:
        flash(f'Quiz with ID {quiz_id} not found.', 'danger')
        return redirect('/quiz_management')

    if request.method == 'POST':
        question_statement = request.form.get('question_statement')
        option_1 = request.form.get('option_1')
        option_2 = request.form.get('option_2')
        option_3 = request.form.get('option_3')
        option_4 = request.form.get('option_4')
        correct_option = request.form.get('correct_option')

        if not all([question_statement, option_1, option_2, option_3, option_4, correct_option]):
            flash('All fields are required!', 'danger')
            return redirect(f'/create_question?quiz_id={quiz_id}')

        try:
            correct_option = int(correct_option)
            if correct_option not in [1, 2, 3, 4]:
                raise ValueError("Invalid option")
        except ValueError:
            flash('Correct option must be a number between 1 and 4.', 'danger')
            return redirect(f'/create_question?quiz_id={quiz_id}')

        options = f"{option_1}|{option_2}|{option_3}|{option_4}"

        new_question = Question(
            quiz_id=quiz_id,
            question_statement=question_statement,
            options=options,
            correct_option=str(correct_option)
        )
        db.session.add(new_question)
        db.session.commit()

        flash('Question added successfully!', 'success')
        return redirect(f'/create_question?quiz_id={quiz_id}')

    return render_template('create_question.html', quiz=quiz, quiz_id=quiz_id)

@app.route('/create_quiz', methods=['GET', 'POST'])
def create_quiz():
    if 'user_id' not in session or not session.get('is_admin'):
        flash('Unauthorized access.', 'danger')
        return redirect('/login')

    chapters = Chapter.query.all()

    if request.method == 'POST':
        print("🔍 Debug: Form Data Received =", request.form.to_dict())  
       
        if 'chapter_id' not in request.form:
            flash('Error: Chapter ID is missing!', 'danger')
            return redirect('/create_quiz')

        name = request.form['name']
        chapter_id = request.form['chapter_id']
        date_of_quiz = request.form['date_of_quiz']
        time_duration = request.form['time_duration']
        remarks = request.form['remarks']

        new_quiz = Quiz(
            name=name,
            chapter_id=int(chapter_id), 
            creator_id=session['user_id'],
            date_of_quiz=datetime.strptime(date_of_quiz, '%Y-%m-%d'),
            time_duration=int(time_duration),
            remarks=remarks
        )
        db.session.add(new_quiz)
        db.session.commit()
        flash('Quiz created successfully!', 'success')
        return redirect('/quiz_management')

    return render_template('create_quiz.html', chapters=chapters)

@app.route('/summary_charts')
def summary_charts():
    if 'user_id' not in session:
        flash('You must be logged in to view this page.', 'danger')
        return redirect('/login')

    subjects = Subject.query.all()
    scores_by_subject = {subject.name: 0 for subject in subjects}
    
    user_scores = Score.query.filter_by(user_id=session['user_id']).all()
    
    for score in user_scores:
        subject_name = score.quiz.chapter.subject.name
        scores_by_subject[subject_name] += score.total_score

    return render_template('summary_charts.html', scores_by_subject=scores_by_subject)

@app.route('/delete_chapter/<int:chapter_id>', methods=['POST'])
def delete_chapter(chapter_id):
    if 'user_id' not in session or not session.get('is_admin'):
        flash('Unauthorized access.', 'danger')
        return redirect('/login')

    chapter = Chapter.query.get(chapter_id)
    if chapter:
        db.session.delete(chapter)
        db.session.commit()
        flash('Chapter deleted successfully!', 'success')
    else:
        flash('Chapter not found.', 'danger')

    return redirect('/admin_dashboard')

@app.route('/edit_chapter/<int:chapter_id>', methods=['GET', 'POST'])
def edit_chapter(chapter_id):
    if 'user_id' not in session or not session.get('is_admin'):
        flash('Unauthorized access.', 'danger')
        return redirect('/login')

    chapter = Chapter.query.get_or_404(chapter_id)
    subjects = Subject.query.all() 

    if request.method == 'POST':
        chapter.subject_id = request.form['subject_id']
        chapter.name = request.form['name']
        chapter.description = request.form['description']

        db.session.commit()
        flash('Chapter updated successfully!', 'success')
        return redirect('/admin_dashboard')

    return render_template('edit_chapter.html', chapter=chapter, subjects=subjects)

@app.route('/quiz_management', methods=['GET', 'POST'])
def quiz_management():
    if 'user_id' not in session or not session.get('is_admin'):
        flash('Unauthorized access.', 'danger')
        return redirect('/login')

    quizzes = Quiz.query.all() 

    if request.method == 'POST':
        search_query = request.form.get('search', "").strip()
        if search_query:
            quizzes = Quiz.query.filter(Quiz.name.ilike(f"%{search_query}%")).all()

    return render_template('quiz_management.html', quizzes=quizzes)


@app.route('/delete_quiz/<int:quiz_id>', methods=['POST'])
def delete_quiz(quiz_id):
    if 'user_id' not in session or not session.get('is_admin'):
        flash('Unauthorized access.', 'danger')
        return redirect('/login')

    quiz = Quiz.query.get_or_404(quiz_id)
    db.session.delete(quiz)
    db.session.commit()
    flash('Quiz deleted successfully!', 'success')
    return redirect('/quiz_management')


@app.route('/edit_question/<int:question_id>', methods=['GET', 'POST'])
def edit_question(question_id):
    if 'user_id' not in session or not session.get('is_admin'):
        flash('Unauthorized access.', 'danger')
        return redirect('/login')

    question = Question.query.get_or_404(question_id)

    if request.method == 'POST':
        question.question_statement = request.form.get('question_statement')
        option_1 = request.form.get('option_1')
        option_2 = request.form.get('option_2')
        option_3 = request.form.get('option_3')
        option_4 = request.form.get('option_4')
        correct_option = request.form.get('correct_option')

        # Ensure all fields are filled
        if not all([question.question_statement, option_1, option_2, option_3, option_4, correct_option]):
            flash('All fields are required!', 'danger')
            return redirect(f'/edit_question/{question_id}')

        try:
            correct_option = int(correct_option)
            if correct_option not in [1, 2, 3, 4]:
                raise ValueError("Invalid option")
        except ValueError:
            flash('Correct option must be a number between 1 and 4.', 'danger')
            return redirect(f'/edit_question/{question_id}')

        question.options = f"{option_1}|{option_2}|{option_3}|{option_4}"
        question.correct_option = str(correct_option)

        db.session.commit()
        flash('Question updated successfully!', 'success')
        return redirect('/quiz_management')

    return render_template('edit_question.html', question=question)


@app.route('/delete_question/<int:question_id>', methods=['POST'])
def delete_question(question_id):
    if 'user_id' not in session or not session.get('is_admin'):
        flash('Unauthorized access.', 'danger')
        return redirect('/login')

    question = Question.query.get_or_404(question_id)
    db.session.delete(question)
    db.session.commit()
    flash('Question deleted successfully!', 'success')
    return redirect('/quiz_management')

@app.route('/search', methods=['POST'])
def search():
    if 'user_id' not in session or not session.get('is_admin'):
        flash('Unauthorized access.', 'danger')
        return redirect('/login')

    search_query = request.form.get('search_query', "").strip()

    if not search_query:
        flash('Please enter a search term.', 'warning')
        return redirect('/admin_dashboard')

    # Search Users, Subjects, and Quizzes
    users = User.query.filter(User.username.ilike(f"%{search_query}%")).all()
    subjects = Subject.query.filter(Subject.name.ilike(f"%{search_query}%")).all()
    quizzes = Quiz.query.filter(Quiz.name.ilike(f"%{search_query}%")).all()

    return render_template('search_results.html', users=users, subjects=subjects, quizzes=quizzes, search_query=search_query)

@app.route('/view_user/<int:user_id>')
def view_user(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('view_user.html', user=user)

@app.route('/view_subject/<int:subject_id>')
def view_subject(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    return render_template('view_subject.html', subject=subject)

@app.route('/view_quiz/<int:quiz_id>')
def view_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    return render_template('view_quiz.html', quiz=quiz)

    
# Initialize Database with Admin User
with app.app_context():
    db.create_all()

    # Create default admin user if not exists
    admin_user = User.query.filter_by(username="admin").first()
    if not admin_user:
        admin_user = User(
            username='admin',
            password='admin123',
            full_name='Administrator',
            dob=datetime(1990, 1, 1),
            is_admin=True
        )
        db.session.add(admin_user)
        db.session.commit()

# Run Flask app
if __name__ == "__main__":
    app.run(debug=True)
