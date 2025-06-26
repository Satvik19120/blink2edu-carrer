# Complete Flask App with Coding Assignment Functionality (Blink2EduCarrer)

from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from datetime import datetime
import subprocess

app = Flask(__name__)
app.secret_key = 'secretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blink2educarrer.db'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
app.app_context().push()
# ---------------------- MODELS ----------------------
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

class CodingAssignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class CodingQuestion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey('coding_assignment.id'))
    question_text = db.Column(db.Text, nullable=False)
    sample_input = db.Column(db.Text)
    sample_output = db.Column(db.Text)
    test_input = db.Column(db.Text)
    test_output = db.Column(db.Text)
    language = db.Column(db.String(20), default="python")

class CodingSubmission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    question_id = db.Column(db.Integer, db.ForeignKey('coding_question.id'))
    code = db.Column(db.Text)
    language = db.Column(db.String(20))
    output = db.Column(db.Text)
    is_correct = db.Column(db.Boolean)

# ---------------------- LOGIN MANAGER ----------------------
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ---------------------- ROUTES ----------------------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            login_user(user)
            return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    student_id = session.get('id')
    student = User.query.get(student_id)
    quizzes = CodingAssignment.query.all()#Quiz.query.all()
    assignments = CodingAssignment.query.all()
    if  not assignments:
        assignments=None
    if not quizzes:
        quizzes=None
    return render_template('dashboard.html', student=student, quizzes=quizzes, assignments=assignments)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/create_assignment', methods=['GET', 'POST'])
@login_required
def create_assignment():
    if request.method == 'POST':
        title = request.form['title']
        assignment = CodingAssignment(title=title, creator_id=current_user.id)
        db.session.add(assignment)
        db.session.commit()
        return redirect(url_for('add_coding_question', assignment_id=assignment.id))
    return render_template('create_assignment.html')

@app.route('/add_coding_question/<int:assignment_id>', methods=['GET', 'POST'])
@login_required
def add_coding_question(assignment_id):
    if request.method == 'POST':
        question_text = request.form['question_text']
        sample_input = request.form['sample_input']
        sample_output = request.form['sample_output']
        test_input = request.form['test_input']
        test_output = request.form['test_output']
        language = request.form['language']
        question = CodingQuestion(
            assignment_id=assignment_id,
            question_text=question_text,
            sample_input=sample_input,
            sample_output=sample_output,
            test_input=test_input,
            test_output=test_output,
            language=language
        )
        db.session.add(question)
        db.session.commit()
    return render_template('add_coding_question.html', assignment_id=assignment_id)

@app.route('/attempt_assignment/<int:assignment_id>')
def attempt_assignment(assignment_id):
    questions = CodingQuestion.query.filter_by(assignment_id=assignment_id).all()
    return render_template('attempt_assignment.html', questions=questions)
#---------------------------------------------------
@app.route('/attempt_Quiz_assignment/<int:quiz_id>')
def attempt_quiz_assignment(quiz_id):
    questions = CodingQuestion.query.filter_by(assignment_id=quiz_id).all()
    return render_template('attempt_assignment.html', questions=questions)
#------------------------------------------------------

"""@app.route('/run_code', methods=['POST'])
def run_code():
    data = request.json
    code = data['code']
    input_data = data['input']
    language = data['language']
    question_id = data.get('question_id')

    question = CodingQuestion.query.get(question_id)
    expected_output = question.test_output.strip()

    if language == "python":
        try:
            result = subprocess.run(
                ["python", "-c", code],#------------["python3", "-c", code],
                input=input_data,  # ✅ No .encode() here
                capture_output=True,
                text=True,  # ✅ This makes input/output work with strings
                timeout=5
            )
            actual_output = result.stdout.strip()

            is_correct = actual_output == expected_output

            return jsonify({
                'output': actual_output,
                'expected_output': expected_output,
                'is_correct': is_correct,
                'error': result.stderr.strip()
            })

        except Exception as e:
            return jsonify({'error': str(e)})
    else:
        return jsonify({'error': 'Only Python is supported in local execution'})
"""
import platform

@app.route('/run_code', methods=['POST'])
def run_code():
    data = request.json
    code = data['code']
    input_data = data['input']
    question_id = data['question_id']
    language = data['language']

    if language == "python":
        try:
            # Get test output from database for comparison
            question = CodingQuestion.query.get(question_id)
            expected_output = question.test_output.strip() if question else ""

            # Platform detection
            python_cmd = "python3" if platform.system() != "Windows" else "python"

            # Run code
            result = subprocess.run(
                [python_cmd, "-c", code],
                input=input_data,
                capture_output=True,
                text=True,
                timeout=5
            )

            actual_output = result.stdout.strip()
            error_output = result.stderr.strip()

            # Compare outputs
            is_correct = (actual_output == expected_output)

            # Check if the submission already exists
            existing_submission = CodingSubmission.query.filter_by(
                user_id=current_user.id, 
                question_id=question_id
            ).first()

            if existing_submission:
                # Update the existing record
                existing_submission.code = code
                existing_submission.language = language
                existing_submission.output = actual_output
                existing_submission.is_correct = is_correct
            else:
                # Add new record if it doesn't exist
                submission = CodingSubmission(
                    user_id=current_user.id,
                    question_id=question_id,
                    code=code,
                    language=language,
                    output=actual_output,
                    is_correct=is_correct
                )
                db.session.add(submission)

            # Commit the changes
            db.session.commit()

            return jsonify({
                'output': actual_output,
                'error': error_output,
                'is_correct': is_correct,
                'expected_output': expected_output
            })

        except Exception as e:
            return jsonify({'error': str(e)}), 500
    else:
        return jsonify({'error': 'Only Python is supported in local execution'})


@app.route('/submit_code', methods=['POST'])
@login_required
def submit_code():
    data = request.json
    submission = CodingSubmission(
        user_id=current_user.id,
        question_id=data['question_id'],
        code=data['code'],
        language=data['language'],
        output=data['output'],
        is_correct=data['is_correct']
    )
    db.session.add(submission)
    db.session.commit()
    return jsonify({'message': 'Submission saved'})

# ---------------------- INIT ----------------------
if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)