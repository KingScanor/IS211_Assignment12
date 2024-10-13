#Assignment 12
import sqlite3
from flask import Flask, redirect, render_template, request,g , session

app = Flask(__name__)
app.secret_key = 'IS211_Assignment12'
DATABASE = 'hw12.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'Password1':
            session['logged_in'] = True
            return redirect('/dashboard')
        else:
            error = 'Invalid username or password'
            return render_template('login.html', error=error)
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect('/login')

    cursor = get_db().cursor()
    cursor.execute('select * from Students')
    students = cursor.fetchall()
    cursor.execute("select * from Quizzes")
    quizzes = cursor.fetchall()

    return render_template('dashboard.html', students=students, quizzes=quizzes)

@app.route('/student/add', methods=['GET', 'POST'])
def add_student():
    if not session.get('logged_in'):
        return redirect('/login')

    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        try:
            cursor = get_db().cursor()
            cursor.execute("INSERT INTO Students (first_name, last_name) VALUES (?, ?)", (first_name, last_name))
            get_db().commit()
            return redirect('/dashboard')
        except Exception as e:
            error = 'Error Adding Student'
            return render_template('add_student.html', error=error)

    return render_template('add_student.html')

@app.route('/quiz/add', methods=['GET', 'POST'])
def add_quiz():
    if not session.get('logged_in'):
        return redirect('/login')

    if request.method == 'POST':
        subject = request.form['subject']
        num_questions = request.form['num_questions']
        quiz_date = request.form['quiz_date']
        try:
            cursor = get_db().cursor()
            cursor.execute("INSERT INTO Quizzes (subject, num_questions, quiz_date) VALUES (?, ?, ?)", (subject, num_questions, quiz_date))
            get_db().commit()
            return redirect('/dashboard')
        except Exception as e:
            error = 'Error Adding Quiz'
            return render_template('add_quiz.html', error=error)

    return render_template('add_quiz.html')

@app.route('/student/<int:id>')
def student_results(id):
    if not session.get('logged_in'):
        return redirect('/login')

    cursor = get_db().cursor()
    cursor.execute("SELECT q.id, r.score FROM Quizzes q JOIN Results r ON q.id = r.quiz_id WHERE r.student_id = ?", (id,))
    results = cursor.fetchall()

    return render_template('student_results.html', student_id=id, results=results)

@app.route('/results/add', methods=['GET', 'POST'])
def add_result():
    if not session.get('logged_in'):
        return redirect('/login')

    cursor = get_db().cursor()
    cursor.execute("SELECT id, first_name, last_name FROM Students")
    students = cursor.fetchall()
    cursor.execute("SELECT id, subject FROM Quizzes")
    quizzes = cursor.fetchall()

    if request.method == 'POST':
        student_id = request.form['student_id']
        quiz_id = request.form['quiz_id']
        score = request.form['score']
        try:
            cursor = get_db().cursor()
            cursor.execute("INSERT INTO Results (student_id, quiz_id, score) VALUES (?, ?, ?)", (student_id, quiz_id, score))
            get_db().commit()
            return redirect('/dashboard')
        except Exception as e:
            error = 'Error Adding Result'
            return render_template('add_result.html', students=students, quizzes=quizzes, error=error)

    return render_template('add_result.html', students=students, quizzes=quizzes)

if __name__ == '__main__':
    app.run(debug=True)




