import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from flask import Flask, render_template, request, redirect, flash, session, url_for
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
db.init_app(app)

# Models:

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


# Subject Model
class Subject(db.Model):
    __tablename__ = 'subject'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    chapters = db.relationship('Chapter', backref='subject', lazy=True)

# Chapter Model
class Chapter(db.Model):
    __tablename__ = 'chapter'
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'))
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    quizzes = db.relationship('Quiz', backref='chapter', lazy=True)

# Quiz Model
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

# Question Model
class Question(db.Model):
    __tablename__ = 'question'
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'))
    question_statement = db.Column(db.Text, nullable=False)
    options = db.Column(db.Text, nullable=False)
    correct_option = db.Column(db.String(50), nullable=False)

# Score Model
class Score(db.Model):
    __tablename__ = 'score'
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    time_stamp_of_attempt = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    total_score = db.Column(db.Integer, nullable=False)
    user = db.relationship('User', back_populates='scores')




# Routes:

# General Routes
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

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect('/')


# Admin Routes

@app.route('/admin_dashboard')
def admin_dashboard():
    if 'user_id' not in session or not session.get('is_admin'):
        flash('Unauthorized access.', 'danger')
        return redirect('/login')

    subjects = Subject.query.all() 
    return render_template('admin_dashboard.html', subjects=subjects)

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


@app.route('/search', methods=['POST'])
def search():
    if 'user_id' not in session or not session.get('is_admin'):
        flash('Unauthorized access.', 'danger')
        return redirect('/login')

    search_query = request.form.get('search_query', "").strip()

    if not search_query:
        flash('Please enter a search term.', 'warning')
        return redirect('/admin_dashboard')

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




# User Routes:

@app.route('/user_dashboard')
def user_dashboard():
    if 'user_id' not in session:
        flash('Unauthorized access.', 'danger')
        return redirect('/login')

    user = User.query.get(session['user_id'])
    upcoming_quizzes = Quiz.query.filter(Quiz.date_of_quiz >= datetime.utcnow()).all()

    attempted_quizzes = {score.quiz_id for score in Score.query.filter_by(user_id=user.id).all()}

    return render_template('user_dashboard.html', user=user, upcoming_quizzes=upcoming_quizzes, attempted_quizzes=attempted_quizzes)

@app.route('/user_search', methods=['POST'])
def user_search():
    if 'user_id' not in session:
        flash('Unauthorized access.', 'danger')
        return redirect('/login')

    search_query = request.form.get('search_query')

    if not search_query:
        flash("Please enter a search query.", "warning")
        return redirect(request.referrer)

    # Search Subjects
    subjects = Subject.query.filter(
        Subject.name.ilike(f"%{search_query}%") | 
        Subject.description.ilike(f"%{search_query}%")
    ).all()

    # Search Quizzes
    quizzes = Quiz.query.filter(
        Quiz.name.ilike(f"%{search_query}%") | 
        Quiz.date_of_quiz.like(f"%{search_query}%")
    ).all()

    # Search Scores
    scores = Score.query.join(Quiz).filter(
        (Quiz.name.ilike(f"%{search_query}%")) | 
        (Score.total_score == search_query)
    ).all()

    return render_template(
        'user_search_results.html',
        search_query=search_query,
        subjects=subjects,
        quizzes=quizzes,
        scores=scores
    )

@app.route('/quiz_results/<int:quiz_id>')
def quiz_results(quiz_id):
    if 'user_id' not in session:
        flash('Unauthorized access.', 'danger')
        return redirect('/login')

    user_id = session['user_id']

    quiz = Quiz.query.get_or_404(quiz_id)

    score = Score.query.filter_by(user_id=user_id, quiz_id=quiz_id).first()

    if not score:
        flash("You haven't attempted this quiz yet!", "warning")
        return redirect('/user_scores')

    return render_template('quiz_results.html', quiz=quiz, score=score)


@app.route('/view_quiz_user/<int:quiz_id>')
def view_quiz_user(quiz_id):
    if 'user_id' not in session:
        flash('Unauthorized access.', 'danger')
        return redirect('/login')

    quiz = Quiz.query.get_or_404(quiz_id)
    return render_template('view_quiz_user.html', quiz=quiz)

@app.route('/view_subject_user/<int:subject_id>')
def view_subject_user(subject_id):
    if 'user_id' not in session:
        flash('Unauthorized access.', 'danger')
        return redirect('/login')

    subject = Subject.query.get_or_404(subject_id)

    return render_template('view_subject_user.html', subject=subject)



@app.route('/start_quiz/<int:quiz_id>', methods=['GET', 'POST'])
def start_quiz(quiz_id):
    if 'user_id' not in session:
        flash('Unauthorized access.', 'danger')
        return redirect('/login')

    user_id = session['user_id']
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = quiz.questions

    existing_attempt = Score.query.filter_by(user_id=user_id, quiz_id=quiz_id).first()
    if existing_attempt:
        flash('You have already attempted this quiz. You cannot attempt it again.', 'warning')
        return redirect('/user_dashboard')

    question_no = request.args.get('q_no', '1')
    try:
        question_no = int(question_no)
    except ValueError:
        question_no = 1

    if question_no > len(questions):
        return redirect(url_for('submit_quiz', quiz_id=quiz_id))

    question = questions[question_no - 1]
    last_question = (question_no == len(questions)) 

    return render_template(
        'start_quiz.html',
        quiz=quiz,
        question=question,
        question_no=question_no,
        last_question=last_question
    )

@app.route('/save_answer/<int:quiz_id>/<int:question_id>', methods=['POST'])
def save_answer(quiz_id, question_id):
    if 'user_id' not in session:
        flash('Unauthorized access.', 'danger')
        return redirect('/login')

    selected_option = request.form.get('selected_option')

    if not selected_option:
        flash('Please select an option before proceeding.', 'warning')
        return redirect(url_for('start_quiz', quiz_id=quiz_id, q_no=1))

    try:
        selected_option = int(selected_option)
    except ValueError:
        flash("Invalid selection. Please choose a valid option.", "danger")
        return redirect(url_for('start_quiz', quiz_id=quiz_id, q_no=1))

    session.setdefault('quiz_attempts', {})
    session['quiz_attempts'].setdefault(str(quiz_id), {})
    session['quiz_attempts'][str(quiz_id)][str(question_id)] = selected_option 
    session.modified = True  

    quiz = Quiz.query.get_or_404(quiz_id)
    total_questions = len(quiz.questions)

    q_no_str = request.args.get('q_no', '1') 
    try:
        current_question_no = int(q_no_str)
    except ValueError:
        current_question_no = 1 
 
    if current_question_no >= total_questions:
        return redirect(url_for('submit_quiz', quiz_id=quiz_id))

    next_question_no = current_question_no + 1
    return redirect(url_for('start_quiz', quiz_id=quiz_id, q_no=next_question_no))

@app.route('/submit_quiz/<int:quiz_id>')
def submit_quiz(quiz_id):
    if 'user_id' not in session:
        flash('Unauthorized access.', 'danger')
        return redirect('/login')

    user_id = session['user_id']
    quiz = Quiz.query.get_or_404(quiz_id)
    total_questions = len(quiz.questions)
    correct_answers = 0

    for question in quiz.questions:
        correct_option = int(question.correct_option) 
        user_answer = session.get('quiz_attempts', {}).get(str(quiz_id), {}).get(str(question.id))

        if user_answer is not None and int(user_answer) == correct_option:
            correct_answers += 1

    new_score = Score(user_id=user_id, quiz_id=quiz_id, total_score=correct_answers)
    db.session.add(new_score)
    db.session.commit()

    session.get('quiz_attempts', {}).pop(str(quiz_id), None)

    flash("Quiz Submitted Successfully!", "success")
    return redirect(url_for('user_scores'))


@app.route('/user_scores')
def user_scores():
    if 'user_id' not in session:
        flash('Unauthorized access.', 'danger')
        return redirect('/login')

    user_id = session['user_id']
    user_scores = Score.query.filter_by(user_id=user_id).all()

    return render_template('user_scores.html', user_scores=user_scores)


# Routes for Summary Pages

@app.route('/generate_user_charts')
def generate_user_charts():
    if 'user_id' not in session:
        flash('Unauthorized access.', 'danger')
        return redirect('/login')

    import matplotlib
    matplotlib.use('Agg') 
    import matplotlib.pyplot as plt

    user_id = session['user_id']

    if not os.path.exists("static/images"):
        os.makedirs("static/images")

    user_scores = Score.query.filter_by(user_id=user_id).all()

    subject_scores = {}
    for score in user_scores:
        subject_name = score.quiz.chapter.subject.name
        subject_scores[subject_name] = subject_scores.get(subject_name, 0) + score.total_score

    monthly_attempts = {}
    for score in user_scores:
        month = score.quiz.date_of_quiz.strftime('%b %Y') 
        monthly_attempts[month] = monthly_attempts.get(month, 0) + 1

    plt.figure(figsize=(6, 4))
    plt.bar(subject_scores.keys(), subject_scores.values(), color='skyblue')
    plt.xlabel("Subjects")
    plt.ylabel("Total Score")
    plt.title("User Scores per Subject")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig("static/images/user_scores_chart.png")
    plt.close()

    plt.figure(figsize=(6, 4))
    plt.pie(monthly_attempts.values(), labels=monthly_attempts.keys(), autopct='%1.1f%%', colors=['#FF6384', '#36A2EB', '#FFCE56', '#4CAF50'])
    plt.title("Quizzes Attempted per Month")
    plt.savefig("static/images/user_attempts_chart.png")
    plt.close()

    return redirect('/user_summary')


@app.route('/generate_charts')
def generate_charts():
    if 'user_id' not in session or not session.get('is_admin'):
        flash('Unauthorized access.', 'danger')
        return redirect('/login')

    import matplotlib
    matplotlib.use('Agg') 
    import matplotlib.pyplot as plt

    if not os.path.exists("static/images"):
        os.makedirs("static/images")

    subjects = Subject.query.all()
    top_scorers = []
    scores = []

    for subject in subjects:
        top_score = db.session.query(Score.total_score)\
            .join(Quiz, Score.quiz_id == Quiz.id)\
            .join(Chapter, Quiz.chapter_id == Chapter.id)\
            .join(Subject, Chapter.subject_id == Subject.id)\
            .filter(Subject.id == subject.id)\
            .order_by(Score.total_score.desc()).first()

        if top_score:
            top_scorers.append(subject.name)
            scores.append(top_score[0])

    plt.figure(figsize=(6, 4))
    plt.bar(top_scorers, scores, color='skyblue')
    plt.xlabel("Subjects")
    plt.ylabel("Top Score")
    plt.title("Top Scorers per Subject")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig("static/images/top_scorers_chart.png")
    plt.close()

    subject_attempts = []
    attempts = []
    for subject in subjects:
        count_attempts = db.session.query(Score.id)\
            .join(Quiz, Score.quiz_id == Quiz.id)\
            .join(Chapter, Quiz.chapter_id == Chapter.id)\
            .join(Subject, Chapter.subject_id == Subject.id)\
            .filter(Subject.id == subject.id).count()

        if count_attempts > 0:
            subject_attempts.append(subject.name)
            attempts.append(count_attempts)

    plt.figure(figsize=(6, 4))
    plt.pie(attempts, labels=subject_attempts, autopct='%1.1f%%', colors=['#FF6384', '#36A2EB', '#FFCE56', '#4CAF50'])
    plt.title("User Attempts per Subject")
    plt.savefig("static/images/admin_attempts_chart.png") 
    plt.close()

    return redirect('/admin_summary')

@app.route('/user_summary')
def user_summary():
    if 'user_id' not in session:
        flash('Unauthorized access.', 'danger')
        return redirect('/login')

    user_id = session['user_id']

    subjects = {}
    scores = {}

    user_scores = Score.query.filter_by(user_id=user_id).all()

    for score in user_scores:
        subject_name = score.quiz.chapter.subject.name
        subjects[subject_name] = subjects.get(subject_name, 0) + score.total_score
        scores[subject_name] = scores.get(subject_name, 0) + 1  

    subject_labels = list(subjects.keys())
    subject_scores = list(subjects.values())

    months = {}
    for score in user_scores:
        month = score.quiz.date_of_quiz.strftime('%B') 
        months[month] = months.get(month, 0) + 1 

    month_labels = list(months.keys())
    month_quizzes = list(months.values())

    return render_template(
        'user_summary.html',
        subjects=subject_labels,
        scores=subject_scores,
        months=month_labels,
        quizzes=month_quizzes
    )


@app.route('/admin_summary')
def admin_summary():
    if 'user_id' not in session or not session.get('is_admin'):
        flash('Unauthorized access.', 'danger')
        return redirect('/login')

    top_scorers = {}
    subject_attempts = {}

    all_scores = Score.query.all()

    for score in all_scores:
        subject_name = score.quiz.chapter.subject.name

        if subject_name not in top_scorers or score.total_score > top_scorers[subject_name]:
            top_scorers[subject_name] = score.total_score

        subject_attempts[subject_name] = subject_attempts.get(subject_name, 0) + 1

    top_scorer_labels = list(top_scorers.keys())
    top_scorer_scores = list(top_scorers.values())

    subject_labels = list(subject_attempts.keys())
    subject_counts = list(subject_attempts.values())

    return render_template(
        'admin_summary.html',
        top_scorers=top_scorer_labels,
        scores=top_scorer_scores,
        subjects=subject_labels,
        attempts=subject_counts
    )



# Initializing Database with Admin User
with app.app_context():
    db.create_all()

    # Creating default admin user if not exists
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
