# Complete Flask App with Coding Assignment Functionality (Blink2EduCarrer)

from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from datetime import datetime
import subprocess
#---------------------------------------------
import platform

import subprocess
import platform
import os
import uuid
from flask import Flask, request, jsonify
#from models import CodingQuestion, CodingSubmission
from flask_login import current_user


app = Flask(__name__)
app.secret_key = 'secretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blink2educarrer_03.db'
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
        existinguser = User.query.filter_by(username=username).first()
        if existinguser:
            return redirect(url_for('index'))
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            login_user(user)
            return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/dashboard')
@login_required
def dashboard():
    #student_id = session.get('id')
    student = User.query.filter_by(id=current_user.id).first()
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
    return redirect(url_for('index'))

@app.route('/create_assignment', methods=['GET', 'POST'])
@login_required
def create_assignment():
    quizzes = CodingAssignment.query.filter_by(creator_id=current_user.id).all()#Quiz.query.all()
    assignments = CodingAssignment.query.filter_by(creator_id=current_user.id).all()
    if request.method == 'POST':
        title = request.form['title']
        assignment = CodingAssignment(title=title, creator_id=current_user.id)
        db.session.add(assignment)
        db.session.commit()
        return redirect(url_for('add_coding_question', assignment_id=assignment.id))
    return render_template('create_assignment.html', quizzes = quizzes, assignments = assignments)

@app.route('/add_coding_question/<int:assignment_id>', methods=['GET', 'POST'])
@login_required
def add_coding_question(assignment_id):
    if request.method == 'POST':
        question_text = request.form['question_text']
        sample_input = request.form['sample_input']
        sample_output = request.form['sample_output']
        test_input = request.form['test_input']
        test_output = request.form['test_output']
        language = None
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

@app.route('/assignment/edit/<int:assignment_id>', methods=['GET', 'POST'])
@login_required
def edit_assignment(assignment_id):
    assignment = CodingAssignment.query.get_or_404(assignment_id)
    questions = CodingQuestion.query.filter_by(assignment_id=assignment_id).all()

    # Ensure current user owns the assignment
    if assignment.creator_id != current_user.id:
        return redirect(url_for('create_assignment'))
    
    if request.method == 'POST':
        assignment.title = request.form.get('title')
        db.session.commit()
        return redirect(url_for('create_assignment'))
    
    return render_template('edit_assignment.html', assignment=assignment, questions = questions)

@app.route('/assignment/delete/<int:assignment_id>', methods=['POST'])
@login_required
def delete_assignment(assignment_id):
    assignment = CodingAssignment.query.get_or_404(assignment_id)
    
    if assignment.creator_id != current_user.id:
        return redirect(url_for('create_assignment'))
    
    db.session.delete(assignment)
    db.session.commit()
    return redirect(url_for('create_assignment'))


@app.route('/edit_coding_question/<int:question_id>', methods=['POST'])
def edit_coding_question(question_id):
    question = CodingQuestion.query.get_or_404(question_id)
    question.question_text = request.form['question_text']
    question.sample_input = request.form['sample_input']
    question.sample_output = request.form['sample_output']
    question.test_input = request.form['test_input']
    question.test_output = request.form['test_output']

    #question = CodingQuestion.query.get_or_404(question_id)

    # data = request.json  # Assuming JSON data is sent
    # question.question_text = data.get('question_text', question.question_text)
    # question.sample_input = question.sample_input
    # question.sample_output = question.sample_output
    # question.test_input = question.test_input
    # question.test_output = question.test_output
    # question.language = question.language
    db.session.commit()
    return jsonify({'message': 'Question updated successfully'})

@app.route('/delete_question/<int:question_id>', methods=['DELETE'])
def delete_question(question_id):
    question = CodingQuestion.query.get_or_404(question_id)
    db.session.delete(question)
    db.session.commit()
    
    return jsonify({'message': 'Question deleted successfully'})


@app.route('/attempt_assignment/<int:assignment_id>')
def attempt_assignment(assignment_id):
    questions = CodingQuestion.query.filter_by(assignment_id=assignment_id).all()
    assignment = CodingQuestion.query.filter_by(assignment_id=assignment_id).first()
    return render_template('attempt_assignment.html', questions=questions, assignment=assignment)
#---------------------------------------------------
@app.route('/attempt_Quiz_assignment/<int:quiz_id>')
def attempt_quiz_assignment(quiz_id):
    questions = CodingQuestion.query.filter_by(assignment_id=quiz_id).all()
    return render_template('attempt_assignment.html', questions=questions)
#------------------------------------------------------


# ========================
# Quiz Routes
# ========================

@app.route('/quiz/edit/<int:quiz_id>', methods=['GET', 'POST'])
@login_required
def edit_quiz(quiz_id):
    quiz = CodingAssignment.query.get_or_404(quiz_id)
    questions = CodingQuestion.query.filter_by(assignment_id=quiz_id).all()
    if quiz.creator_id != current_user.id:
        return redirect(url_for('create_assignment'))
        #abort(403)
    
    if request.method == 'POST':
        quiz.title = request.form.get('title')
        db.session.commit()
        return redirect(url_for('create_assignment'))
    
    return render_template('edit_assignment.html', assignment=quiz, questions = questions)

@app.route('/quiz/delete/<int:quiz_id>', methods=['POST'])
@login_required
def delete_quiz(quiz_id):
    quiz = CodingAssignment.query.get_or_404(quiz_id)
    
    if quiz.creator_id != current_user.id:
        #abort(403)
        return redirect(url_for('create_assignment'))
    
    db.session.delete(quiz)
    db.session.commit()
    return redirect(url_for('create_assignment'))
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

import subprocess
import platform
import os
import uuid
from flask import Flask, request, jsonify
#from models import CodingQuestion, CodingSubmission
from flask_login import current_user



@app.route('/run_code', methods=['POST'])
def run_code():
    data = request.json
    code = data['code']
    question_id = data['question_id']
    #------------------------------------------------------------------
    #language = data['language']
    #---------------------------------------------
    try:
        # Get test cases from database
        question = CodingQuestion.query.get(question_id)
        #language=question.language
        language = data['language']
        test_inputs = question.test_input.strip().split("\n") if question else []
        expected_outputs = question.test_output.strip().split("\n") if question else []

        if len(test_inputs) != len(expected_outputs):
            return jsonify({'error': 'Mismatch in test cases count'}), 500

        results = []
        all_correct = True

        for test_input, expected_output in zip(test_inputs, expected_outputs):
            actual_output, error_output = None, None

            if language == "python":
                python_cmd = "python3" if platform.system() != "Windows" else "python"
                result = subprocess.run(
                    [python_cmd, "-c", code],
                    input=test_input,
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                actual_output = result.stdout.strip()
                error_output = result.stderr.strip()

            elif language == "java":
                #temp_file_name = f"TempProgram_{uuid.uuid4().hex}.java"
                class_name = "Main"
                temp_file_name = f"{class_name}.java"
                with open(temp_file_name, "w") as f:
                    f.write(code)

                compile_process = subprocess.run(["javac", temp_file_name], capture_output=True, text=True)
                if compile_process.returncode != 0:
                    error_output = compile_process.stderr
                else:
                    run_process = subprocess.run(["java", class_name], capture_output=True, text=True, input=test_input, timeout=5)
                    actual_output = run_process.stdout.strip()
                    error_output = run_process.stderr.strip()
                    error_output = "\n".join(
                        line for line in run_process.stderr.strip().splitlines()
                        if "Picked up JAVA_TOOL_OPTIONS" not in line
                    )

                os.remove(temp_file_name)
                if os.path.exists(f"{class_name}.class"):
                    os.remove(f"{class_name}.class")

            elif language == "c":
                #temp_file_name = f"program_{uuid.uuid4().hex}.c"
                #executable_name = "program"
                executable_name = "main"
                temp_file_name = f"{executable_name}.c"
                with open(temp_file_name, "w") as f:
                    f.write(code)

                compile_process = subprocess.run(["gcc", temp_file_name, "-o", executable_name], capture_output=True, text=True)
                if compile_process.returncode != 0:
                    error_output = compile_process.stderr
                else:
                    run_process = subprocess.run([f"./{executable_name}"], capture_output=True, text=True, input=test_input, timeout=5)
                    actual_output = run_process.stdout.strip()
                    error_output = run_process.stderr.strip()

                os.remove(temp_file_name)
                if os.path.exists(executable_name):
                    os.remove(executable_name)

            elif language == "cpp":
                temp_file_name = f"program_{uuid.uuid4().hex}.cpp"
                executable_name = "program"

                with open(temp_file_name, "w") as f:
                    f.write(code)

                compile_process = subprocess.run(["g++", temp_file_name, "-o", executable_name], capture_output=True, text=True)
                if compile_process.returncode != 0:
                    error_output = compile_process.stderr
                else:
                    run_process = subprocess.run([f"./{executable_name}"], capture_output=True, text=True, input=test_input, timeout=5)
                    actual_output = run_process.stdout.strip()
                    error_output = run_process.stderr.strip()

                os.remove(temp_file_name)
                if os.path.exists(executable_name):
                    os.remove(executable_name)

            #elif language == "javascript":
                #result = subprocess.run(["node", "-e", code], input=test_input, capture_output=True, text=True, timeout=5)
                #result = subprocess.run(["node", "-e", code], capture_output=True, text=True, input=test_input, timeout=5)
                #actual_output = result.stdout.strip()
                #error_output = result.stderr.strip()
            
            elif language == "javascript":
                temp_file_name = "temp_script.js"
                
                js_code = """
                process.stdin.on("data", function (data){
                    console.log(data.toString().trim());
                });"""

                # Write JavaScript code to a temporary file
                with open(temp_file_name, "w") as f:
                    f.write(code)
            
                try:
                    # Run the JavaScript file using Node.js
                    result = subprocess.run(
                        ["node", temp_file_name],
                        capture_output=True,
                        text=True,
                        input=test_input,
                        timeout=5
                    )

                    actual_output = result.stdout.strip()
                    error_output = result.stderr.strip()
                    print("---o-u-t----p-u-t-",actual_output)
                except subprocess.TimeoutExpired:
                    error_output = "Error: Execution timed out."

                except Exception as e:
                    error_output = f"Error: {str(e)}"

                finally:
                    # Cleanup temporary file
                    print("---------error_outtput---",error_output)
                    os.remove(temp_file_name)

            elif language == "ruby":
                result = subprocess.run(["ruby", "-e", code], input=test_input, capture_output=True, text=True, timeout=5)
                actual_output = result.stdout.strip()
                error_output = result.stderr.strip()

            else:
                return jsonify({'error': 'Unsupported language'}), 400

            is_correct = (actual_output == expected_output)
            results.append({
                'input': test_input,
                'output': actual_output,
                'expected_output': expected_output,
                'is_correct': is_correct,
                'error': error_output
            })

            if not is_correct:
                all_correct = False

        submission = CodingSubmission(
            user_id=current_user.id,
            question_id=question_id,
            code=code,
            language=language,
            output=str(results),  # Save results as string
            is_correct=all_correct
        )
        db.session.add(submission)
        db.session.commit()
        print("-----L-A--N-G-U-A--G-E--",language)
        return jsonify({'test_results': results, 'all_correct': all_correct})

    except Exception as e:
        return jsonify({'error': str(e)}), 500
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




@app.route('/get_next_question/<int:current_id>')
def get_next_question(current_id):
    current_question = CodingQuestion.query.get(current_id)
    if not current_question:
        return jsonify({'error': 'Current question not found'}), 404

    next_question = CodingQuestion.query.filter(
        CodingQuestion.assignment_id == current_question.assignment_id,
        CodingQuestion.id > current_id
    ).order_by(CodingQuestion.id.asc()).first()

    if not next_question:
        return jsonify({'message': 'No more questions in this assignment'}), 200

    return jsonify({
        'id': next_question.id,
        'question_text': next_question.question_text,
        'sample_input': next_question.sample_input,
        'sample_output': next_question.sample_output
    })


@app.route('/api/question/<int:id>')
def get_question(id):
    question = CodingQuestion.query.get(id)
    if question:
        return jsonify({
            'title': question.title,
            'description': question.description,
            'sample_input': question.sample_input,
            'sample_output': question.sample_output
        })
    return jsonify({'error': 'Question not found'}), 404




#------LEADERBOARD-----------LEADERBOARD---------------LEADERBOARD-------
from sqlalchemy import func

def get_leaderboard(assignment_id):
    # Get all questions for this assignment
    question_ids = [q.id for q in CodingQuestion.query.filter_by(assignment_id=assignment_id).all()]
    # Aggregate correct submissions per user
    leaderboard = (
        db.session.query(
            User.username,
            func.count(CodingSubmission.id).label('correct_count')
        )
        .join(CodingSubmission, CodingSubmission.user_id == User.id)
        .filter(
            CodingSubmission.question_id.in_(question_ids),
            CodingSubmission.is_correct == True
        )
        .group_by(User.id)
        .order_by(func.count(CodingSubmission.id).desc())
        .all()
    )
    return leaderboard

@app.route('/leaderboard_assignment/<int:assignment_id>')
@login_required
def leaderboard_assignment(assignment_id):
    leaderboard = get_leaderboard(assignment_id)
    assignment = CodingAssignment.query.get_or_404(assignment_id)
    student = User.query.filter_by(id=current_user.id).first()
    return render_template('leaderboard.html', leaderboard=leaderboard, assignment=assignment, student = student)

with app.app_context():
    db.create_all()

# ---------------------- INIT ----------------------
if __name__ == '__main__':
    app.run(debug=True)