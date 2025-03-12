# Quiz Master App

## Author
**Name:** Krish Gupta  
**Roll Number:** 23f2000792  
**Email:** 23f2000792@ds.study.iitm.ac.in  
**Institution:** IIT Madras, BS in Data Science and Applications

---

## Description
Quiz Master is a web-based quiz management system that enables admins to create and manage quizzes, while users can register, attempt quizzes, and track their scores. The project focuses on database structuring, secure API implementation, and a user-friendly interface.

---

## Technologies Used
- **Flask** - Python web framework
- **Flask-SQLAlchemy** - ORM for database management
- **SQLite** - File-based database
- **Matplotlib** - Data visualization for quiz results
- **Flask-Session** - User session management
- **HTML, CSS** - Frontend design
- **Jinja2** - Templating for dynamic content
- **Datetime** - Handling timestamps in quiz attempts

---

## Features
### Default Features
- **User Authentication** - Secure login and registration
- **Quiz Management** - Users can take quizzes; admins can create and manage quizzes
- **Score Tracking** - Users can view and analyze their quiz scores
- **Subject & Chapter Management** - Admins can manage subjects and chapters

### Additional Features
- **Search Functionality** - Users can search for quizzes and subjects
- **User & Admin Dashboards** - Interactive dashboards for insights
- **Dynamic Quiz System** - Engaging and interactive quiz experience

---

## Database Schema
### User Table
- `id`: Primary Key
- `username`: Unique, not null
- `password`: Not null
- `full_name`: Not null
- `qualification`: Nullable
- `dob`: Not null
- `is_admin`: Boolean, default False

### Subject Table
- `id`: Primary Key
- `name`: Not null
- `description`: Nullable

### Chapter Table
- `id`: Primary Key
- `subject_id`: Foreign Key (Subject)
- `name`: Not null
- `description`: Nullable

### Quiz Table
- `id`: Primary Key
- `name`: Not null
- `chapter_id`: Foreign Key (Chapter)
- `creator_id`: Foreign Key (User)
- `date_of_quiz`: Not null
- `time_duration`: Not null
- `remarks`: Nullable

### Question Table
- `id`: Primary Key
- `quiz_id`: Foreign Key (Quiz)
- `question_statement`: Not null
- `options`: Not null
- `correct_option`: Not null

### Score Table
- `id`: Primary Key
- `quiz_id`: Foreign Key (Quiz)
- `user_id`: Foreign Key (User)
- `time_stamp_of_attempt`: Not null
- `total_score`: Not null

---

## API Endpoints
### User Authentication
- `/register` - User Registration
- `/login` - User Login
- `/logout` - User Logout

### Admin Functionalities
- `/admin_dashboard` - Admin Dashboard
- `/create_subject` - Create Subjects

### Quiz Management
- `/create_quiz` - Create and manage quizzes
- `/add_question` - Add questions to quizzes
- `/view_quizzes` - Retrieve quizzes for users

### Score Tracking
- `/view_scores` - Retrieve user scores

---

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/Quiz_Master_MAD1.git
   cd quiz-master
   ```
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # For Windows use `venv\Scripts\activate`
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the application:
   ```bash
   python app.py
   ```
5. Open in browser:
   ```
   http://127.0.0.1:5000/
   ```

---

## Video Demo
[Watch the demo](https://drive.google.com/file/d/1EPTSk8-kr3WE4P67ro96SJKSxQssohUE/view?usp=sharing)

---

## License
This project is licensed under the MIT License.
