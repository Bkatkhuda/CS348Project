# importing everything I need
from flask import Flask, render_template, request, redirect, url_for, session, flash

import sqlite3
import csv
import random


app = Flask(__name__)
app.secret_key = '1234'

# SQLite database setup
conn = sqlite3.connect('database.db')

#conn.execute('DROP TABLE IF EXISTS questions')
#conn.execute('DROP TABLE IF EXISTS choices')
#conn.execute('DROP TABLE IF EXISTS students')
#conn.execute('DROP TABLE IF EXISTS student_choices')
#conn.execute('DROP TABLE IF EXISTS teachers')


conn.execute('''
CREATE TABLE IF NOT EXISTS students (
    student_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    password TEXT,
    name TEXT
)
''')

conn.execute('''
CREATE TABLE IF NOT EXISTS teachers (
    teacher_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    password TEXT,
    name TEXT
)
''')

conn.execute('''
CREATE TABLE IF NOT EXISTS questions (
    question_id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic TEXT,
    text TEXT
)
''')

conn.execute('''
CREATE TABLE IF NOT EXISTS choices (
    question_id INTEGER,
    choice_id INTEGER,
    choice_text TEXT,
    correct INTEGER,
    FOREIGN KEY (question_id) REFERENCES questions(question_id),
    PRIMARY KEY (question_id, choice_id)
)
''')

conn.execute('''
CREATE TABLE IF NOT EXISTS student_choices (
    question_id INTEGER,
    choice_id INTEGER,
    student_id INTEGER,
    correct INTEGER,
    FOREIGN KEY (question_id, choice_id, correct) REFERENCES choices(question_id, choice_id, correct),
    FOREIGN KEY (student_id) REFERENCES students(student_id),
    PRIMARY KEY (question_id, choice_id, student_id)
)
''')

# reading in the data from the CSV files and inserting them into the correct tables 
# To add the questions anc choices for the Sun and Moon quiz, uncomment the following 2 blocks of code

'''
with open('questions.csv', 'r') as csv_file:
    csv_reader = csv.reader(csv_file)
    for row in csv_reader:
        topic, text = row
        exists = conn.execute("SELECT COUNT(*) FROM questions WHERE topic = ? AND text = ?", (topic, text)).fetchone()[0]
        if exists == 0:
            conn.execute("INSERT OR IGNORE INTO questions (topic, text) VALUES (?, ?)", (topic, text))
    

with open('choices.csv', 'r') as csv_file:
    csv_reader = csv.reader(csv_file)
    for row in csv_reader:
        question_id, choice_id, choice_text, correct = row
        conn.execute("INSERT OR IGNORE INTO choices (question_id, choice_id, choice_text, correct) VALUES (?, ?, ?, ?)", (question_id, choice_id, choice_text, correct))

'''
conn.commit()
conn.close()

# Function that checks if username exists in the database
def username_exists(username):
    conn = sqlite3.connect('database.db')
    result = conn.execute("SELECT * FROM students WHERE username=?", (username,)).fetchone()
    result2 = conn.execute("SELECT * FROM teachers WHERE username=?", (username,)).fetchone()
    conn.close()

    if (result is not None) or (result2 is not None):
        return result is not None
    
# Function that checks if name exists in the database
def name_exists(name):
    conn = sqlite3.connect('database.db')
    result = conn.execute("SELECT * FROM students WHERE name=?", (name,)).fetchone()
    result2 = conn.execute("SELECT * FROM teachers WHERE name=?", (name,)).fetchone()
    conn.close()

    if (result is not None) or (result2 is not None):
        return result is not None
    
# Function that checks if quiz topic exists in the database
def quiz_exists(topic):
    conn = sqlite3.connect('database.db')
    result = conn.execute("SELECT * FROM questions WHERE topic=?", (topic,)).fetchone()
    conn.close()

    if result is not None:
        return result is not None






@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    if cursor.execute("SELECT COUNT(*) FROM teachers WHERE username = ? AND password = ?", (username, password)).fetchone()[0] > 0:

        cursor.execute('SELECT * FROM teachers WHERE username = ? AND password = ?', (username, password))
        teacher = cursor.fetchone()
        conn.close()
    
        if teacher:
            session['teacher'] = True
            session['teacher_id'] = teacher[0]  # Store the teacher ID in the session
            session['teacher_username'] = teacher[1]  # Store the teacher username in the session
            session['teacher_name'] = teacher[3]  # Store the teacher name in the session

            return redirect(url_for('dashboard'))
        else:
            return "Login failed. Please check your username and password."
    
    else: 
        conn = sqlite3.connect('database.db')
        cur = conn.cursor()
        cur.execute('SELECT * FROM students WHERE username = ? AND password = ?', (username, password))
        student = cur.fetchone()
        conn.close()

        if student:
            session['teacher'] = False
            session['student_id'] = student[0]  # Store the student ID in the session
            session['student_username'] = student[1]  # Store the student username in the session
            session['student_name'] = student[3]  # Store the student name in the session

            return redirect(url_for('dashboard'))
        else:
            return "Login failed. Please check your username and password."

@app.route('/dashboard')
def dashboard():

    if session['teacher']:

        if 'teacher_id' in session:
            name = session['teacher_name']
            return render_template('teacher_dashboard.html', name=name)
        else:
            return redirect(url_for('index'))
    
    else: 

        if 'student_id' in session:
            name = session['student_name']
            return render_template('dashboard.html', name=name)
        else:
            return redirect(url_for('index'))


@app.route('/edit_user_page')
def edit_user_page():
    if 'teacher_username' in session or 'student_username' in session:
        return render_template('edit_user_page.html')
    else:
        return redirect(url_for('index'))
    

@app.route('/edit_user', methods=['POST'])
def edit_user():

    if 'teacher_username' in session or 'student_username' in session:
        
        # Get form data
        new_username = request.form['new_username']
        new_password = request.form['new_password']
        new_name = request.form['new_name']

        if username_exists(new_username):
            return "Username already exists. Please choose a different username."
        
        if name_exists(new_name):
            return "Name already exists. Please choose a different username."
          
        # Update user's information in the database
        conn = sqlite3.connect('database.db')   
        if session['teacher']:
            conn.execute("UPDATE teachers SET username=?, password=?, name=? WHERE teacher_id=?", (new_username, new_password, new_name, session['teacher_id']))
            session['teacher_username'] = new_username
            session['teacher_name'] = new_name
        else: 
            conn.execute("UPDATE students SET username=?, password=?, name=? WHERE student_id=?", (new_username, new_password, new_name, session['student_id']))
            session['student_username'] = new_username
            session['student_name'] = new_name
        conn.commit()
        conn.close()

        # Update session data with new username and name
        
            
        return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('index'))
    


@app.route('/delete_user')
def delete_user():

    if 'teacher_username' in session or 'student_username' in session:

        if session['teacher']:
            teacher_id = session['teacher_id']
            conn = sqlite3.connect('database.db')            
            conn.execute("DELETE FROM teachers WHERE teacher_id=?", (teacher_id,))
        else:
            student_id = session['student_id']
            conn = sqlite3.connect('database.db')            
            conn.execute("DELETE FROM students WHERE student_id=?", (student_id,))
            conn.execute("DELETE FROM student_choices WHERE student_id=?", (student_id,))

        conn.commit()
        conn.close()

        session.clear()  # Clear session data to logout user
    return redirect(url_for('index'))


@app.route('/logout')
def logout():
    if session['teacher']:
        session.pop('teacher_id', None)
        session.pop('teacher_username', None)
        session.pop('teacher_name', None)
    else:
        session.pop('student_id', None)
        session.pop('student_username', None)
        session.pop('student_name', None)

    return redirect(url_for('index'))


@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']
    name = request.form['name']
    is_teacher = request.form.get('is_teacher', False)

    if username_exists(username):
        return "Username already exists. Please choose a different username."
    
    if name_exists(name):
            return "Name already exists. Please choose a different username."

    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    
    if is_teacher:
        cur.execute('INSERT OR IGNORE INTO teachers (username, password, name) VALUES (?, ?, ?)', (username, password, name))
    else:
        cur.execute('INSERT OR IGNORE INTO students (username, password, name) VALUES (?, ?, ?)', (username, password, name))
    conn.commit()
    conn.close()

    return redirect(url_for('index'))



# Student Functions


@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    conn = sqlite3.connect('database.db')
    topics = conn.execute("SELECT DISTINCT topic FROM questions").fetchall()
    conn.close()

    topic_list = []
    for i in topics: 
        topic_list.append(i[0])
    
    if request.method == 'POST':
        selected_topic = request.form['topic']
        
        # Redirect to a route to start the quiz with the selected topic
        return redirect(url_for('start_quiz', topic=selected_topic))
    
    return render_template('quiz.html', topics=topic_list)


@app.route('/start_quiz/<topic>')
def start_quiz(topic):
    conn = sqlite3.connect('database.db')
    questions = conn.execute("SELECT q.text, c.choice_text FROM questions q JOIN choices c ON q.question_id = c.question_id WHERE q.topic=?", (topic,)).fetchall()
    conn.close()

    questions_with_choices = {}
    for question, choice in questions:
        if question not in questions_with_choices:
            questions_with_choices[question] = []
        questions_with_choices[question].append(choice)

    #randomizes question order
    random_order = list(questions_with_choices.items())
    random.shuffle(random_order)
    random_order_dic = dict(random_order)

    #radomizes choices order
    for key in random_order_dic:
        random.shuffle(random_order_dic[key])

    return render_template('start_quiz.html', questions=random_order_dic.items())

@app.route('/submit_quiz', methods=['POST'])
def submit_quiz():
    if request.method == 'POST':
        form_data = request.form
        student_id = session['student_id']  
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
       
        # Loop through form data to insert selected choices into student_choices table

        for question_text, choice_text in form_data.items():
            question_id = cursor.execute("SELECT question_id FROM questions WHERE text=?", (question_text,)).fetchone()[0]
            choice_id = cursor.execute("SELECT c.choice_id FROM choices c, questions q WHERE c.question_id = q.question_id AND q.question_id =? AND c.choice_text=?", (question_id, choice_text)).fetchone()[0]
            correct = cursor.execute("SELECT c.correct FROM choices c, questions q WHERE c.question_id = q.question_id AND q.question_id =? AND c.choice_text=?", (question_id, choice_text)).fetchone()[0]

            if cursor.execute("SELECT COUNT(*) FROM student_choices WHERE question_id = ? AND student_id = ?", (question_id, student_id)).fetchone()[0] > 0:
                cursor.execute("UPDATE student_choices SET choice_id = ?, correct = ? WHERE question_id = ? AND student_id = ?", (choice_id, correct, question_id, student_id))
            else: 
                cursor.execute("INSERT INTO student_choices (question_id, choice_id, student_id, correct) VALUES (?, ?, ?, ?)", (question_id, choice_id, student_id, correct))
        
        conn.commit()
        conn.close()
        return redirect(url_for('dashboard'))


@app.route('/quiz_topic_report', methods=['GET', 'POST'])
def quiz_topic_report():
    if request.method == 'POST':
        # Handle form submission
        topic = request.form['topic']
        show_correct_answers = request.form.get('show_correct_answers', 'No')
        # Perform actions based on user selections (e.g., generate report)
        # Redirect to appropriate route after processing form
        return redirect(url_for('report', topic=topic, show_correct_answers=show_correct_answers))
    
    else:
        # Render the report generation page
        conn = sqlite3.connect('database.db')
        topics = conn.execute("SELECT DISTINCT topic FROM questions").fetchall()
        conn.close()

        topic_list = []
        for i in topics: 
            topic_list.append(i[0])

        return render_template('quiz_topic_report.html', topics=topic_list)
    

@app.route('/report')
def report():
    name = session['student_name']
    student_id = session['student_id']
    topic = request.args.get('topic')

    conn = sqlite3.connect('database.db')

    num_correct = conn.execute("SELECT COUNT(*) FROM student_choices sc NATURAL JOIN questions q WHERE q.topic = ? AND sc.student_id = ? AND sc.correct = 1", (topic, student_id)).fetchone()[0]
    num_questions = conn.execute("SELECT COUNT(*) FROM questions WHERE topic = ?", (topic,)).fetchone()[0]

    if conn.execute("SELECT COUNT(*) FROM student_choices sc NATURAL JOIN questions q WHERE q.topic = ? AND sc.student_id = ?", (topic, student_id)).fetchone()[0] == 0:
        return "Sorry, you have not done this quiz yet!"
    
    conn.close()

    grade = round((num_correct/num_questions) * 100, 2)
    message = ''

    if grade < 40:
        message = "You need to practice more!!"
    elif grade < 70:
        message = "Good Job, try practicing more!"
    elif grade < 90:
        message = "Greate Job, You're Almost there!"
    elif grade < 100:
        message = "Excellent, you are ready, and should move onto the next topic!"

    # Handle report generation based on user selections
    show_correct_answers = request.args.get('show_correct_answers')

    if show_correct_answers == "No":
        # Logic to generate report based on user selections
        return render_template('report.html', topic=topic, show_correct_answers=show_correct_answers, grade = grade, name = name, message = message)
    else: 

        conn = sqlite3.connect('database.db')
        
        questions = conn.execute('''
            SELECT q.text, c.choice_text 
            FROM questions q JOIN choices c ON q.question_id = c.question_id 
            WHERE q.topic=? AND c.correct = 1
            EXCEPT
            SELECT q.text, c.choice_text
            FROM questions q JOIN choices c ON q.question_id = c.question_id JOIN student_choices sc ON sc.question_id = c.question_id AND sc.choice_id = c.choice_id
            WHERE q.topic=? AND sc.student_id = ?''', (topic, topic, session['student_id'])).fetchall()
        
        conn.close()

        questions_with_choices = {}
        for question, answer in questions:
            if question not in questions_with_choices:
                questions_with_choices[question] = []
            questions_with_choices[question].append(answer)
        
        show = ""
        if len(questions_with_choices) == 0:
            show = "You solved everything correctly!"
        
        return render_template('report_answers.html', topic=topic, show_correct_answers=show_correct_answers, grade = grade, name = name, message = message, questions=questions_with_choices.items(), show = show)





# TEACHER METHODS:

@app.route('/teacher_view_students')
def teacher_view_students():
    conn = sqlite3.connect('database.db')
    students = conn.execute("SELECT student_id, username, name FROM students").fetchall()
    conn.close()

    return render_template('teacher_view_students.html', students=students)


@app.route('/teacher_view_quizzes', methods=['GET', 'POST'])
def teacher_view_quizzes():

    conn = sqlite3.connect('database.db')
    topics = conn.execute("SELECT DISTINCT topic FROM questions").fetchall()
    conn.close()

    topic_list = []
    for i in topics: 
        topic_list.append(i[0])
    
    if request.method == 'POST':
        selected_topic = request.form['topic']
        
        # Redirect to a route to view the quiz with the selected topic
        return redirect(url_for('teacher_view_quiz', topic=selected_topic))
    
    return render_template('teacher_view_quizzes.html', topics=topic_list)


@app.route('/teacher_view_quiz/<topic>')
def teacher_view_quiz(topic):
    conn = sqlite3.connect('database.db')
    questions = conn.execute("SELECT q.text, c.choice_text FROM questions q JOIN choices c ON q.question_id = c.question_id WHERE q.topic=?", (topic,)).fetchall()
    conn.close()

    questions_with_choices = {}
    for question, choice in questions:
        if question not in questions_with_choices:
            questions_with_choices[question] = []
        questions_with_choices[question].append(choice)
    
    return render_template('teacher_view_quiz.html', questions=questions_with_choices.items())





@app.route('/teacher_view_student_reports', methods=['GET', 'POST'])
def teacher_view_student_reports():
    # Fetch students and quizzes from the database

    if request.method == "POST":

        student_name = request.form['student']
        student_id = conn.execute("SELECT student_id FROM students WHERE name = ?", (student_name,)).fetchone()[0]
        topic = request.form['topic']

        conn = sqlite3.connect('database.db')

        num_correct = conn.execute("SELECT COUNT(*) FROM student_choices sc NATURAL JOIN questions q WHERE q.topic = ? AND sc.student_id = ? AND sc.correct = 1", (topic, student_id)).fetchone()[0]
        num_questions = conn.execute("SELECT COUNT(*) FROM questions WHERE topic = ?", (topic,)).fetchone()[0]

        if conn.execute("SELECT COUNT(*) FROM student_choices sc NATURAL JOIN questions q WHERE q.topic = ? AND sc.student_id = ?", (topic, student_id)).fetchone()[0] == 0:
            return "Sorry, you have not done this quiz yet!"
        
        conn.close()

        grade = round((num_correct/num_questions) * 100, 2)
        message = ''

        if grade < 40:
            message = "The student needs to practice more!!"
        elif grade < 70:
            message = "The student should try practicing more!"
        elif grade < 90:
            message = "The student did great, they are almost there!"
        elif grade < 100:
            message = "The sudent did excellent, and should move onto the next topic!"        
        
        questions = conn.execute('''
            SELECT q.text, c.choice_text 
            FROM questions q JOIN choices c ON q.question_id = c.question_id 
            WHERE q.topic=? AND c.correct = 1
            EXCEPT
            SELECT q.text, c.choice_text
            FROM questions q JOIN choices c ON q.question_id = c.question_id JOIN student_choices sc ON sc.question_id = c.question_id AND sc.choice_id = c.choice_id
            WHERE q.topic=? AND sc.student_id = ?''', (topic, topic, student_id)).fetchall()
        
        conn.close()

        questions_with_choices = {}
        for question, answer in questions:
            if question not in questions_with_choices:
                questions_with_choices[question] = []
            questions_with_choices[question].append(answer)
        
        show = ""
        if len(questions_with_choices) == 0:
            show = "The student solved everything correctly!"
        
        return render_template('report_answers.html', topic=topic, show_correct_answers='yes', grade = grade, name = student_name, message = message, questions=questions_with_choices.items(), show = show)


    else: 
        conn = sqlite3.connect('database.db')
        students = conn.execute("SELECT DISTINCT name FROM students").fetchall()
        topics = conn.execute("SELECT DISTINCT topic FROM questions").fetchall()

        topic_list = []
        for i in topics: 
            topic_list.append(i[0])

        student_list = []
        for i in students: 
            student_list.append(i[0])

        conn.close()

        return render_template('teacher_view_student_reports.html', students=student_list, topics=topic_list)



@app.route('/generate_report', methods=['POST'])
def generate_report():
        conn = sqlite3.connect('database.db')

        student_name = request.form['student']
        student_id = conn.execute("SELECT student_id FROM students WHERE name = ?", (student_name,)).fetchone()[0]
        topic = request.form['topic']

        num_correct = conn.execute("SELECT COUNT(*) FROM student_choices sc NATURAL JOIN questions q WHERE q.topic = ? AND sc.student_id = ? AND sc.correct = 1", (topic, student_id)).fetchone()[0]
        num_questions = conn.execute("SELECT COUNT(*) FROM questions WHERE topic = ?", (topic,)).fetchone()[0]

        if conn.execute("SELECT COUNT(*) FROM student_choices sc NATURAL JOIN questions q WHERE q.topic = ? AND sc.student_id = ?", (topic, student_id)).fetchone()[0] == 0:
            return "Sorry, The student has not done this quiz yet!"
        

        grade = round((num_correct/num_questions) * 100, 2)
        message = ''

        if grade < 40:
            message = "You need to practice more!!"
        elif grade < 70:
            message = "Good Job, try practicing more!"
        elif grade < 90:
            message = "Greate Job, You're Almost there!"
        elif grade < 100:
            message = "Excellent, you are ready, and should move onto the next topic!"        
        
        questions = conn.execute('''

            SELECT q.text, c.choice_text 
            FROM questions q JOIN choices c ON q.question_id = c.question_id 
            WHERE q.topic=? AND c.correct = 1
            EXCEPT
            SELECT q.text, c.choice_text
            FROM questions q JOIN choices c ON q.question_id = c.question_id JOIN student_choices sc ON sc.question_id = c.question_id AND sc.choice_id = c.choice_id
            WHERE q.topic=? AND sc.student_id = ?''', (topic, topic, student_id)).fetchall()
        
        conn.close()

        questions_with_choices = {}
        for question, answer in questions:
            if question not in questions_with_choices:
                questions_with_choices[question] = []
            questions_with_choices[question].append(answer)
        
        show = ""
        if len(questions_with_choices) == 0:
            show = "The student solved everything correctly!"
        
        return render_template('report_answers.html', topic=topic, show_correct_answers='yes', grade = grade, name = student_name, message = message, questions=questions_with_choices.items(), show = show)




@app.route('/teacher_add_quiz', methods=['GET', 'POST'])
def teacher_add_quiz():
    if request.method == 'POST':
        
        # Get form data
        topic = request.form['topic']
        questions = [request.form['question1'], request.form['question2'], request.form['question3']]

        if quiz_exists(topic):
            return "This quiz topic already exists. Please choose a different topic."

        # Insert quiz details into the database
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        for text in questions: 
            conn.execute("INSERT OR IGNORE INTO questions (topic, text) VALUES (?, ?)", (topic, text))
            conn.commit()

        
        #Adding question 1 choices: 

        question1_id = cursor.execute("SELECT question_id FROM questions WHERE topic = ? AND text = ?", (topic,questions[0])).fetchone()[0]
        question1_choices = [request.form['correct_choice1'], request.form['choice2_1'], request.form['choice3_1'], request.form['choice4_1']]

        for i in range(len(question1_choices)):
            if i == 0:
                conn.execute("INSERT OR IGNORE INTO choices (question_id, choice_id, choice_text, correct) VALUES (?, ?, ?, ?)", (question1_id, i+1, question1_choices[i], 1))
                conn.commit()

            else:
                conn.execute("INSERT OR IGNORE INTO choices (question_id, choice_id, choice_text, correct) VALUES (?, ?, ?, ?)", (question1_id, i+1, question1_choices[i], 0))
                conn.commit()

        #Adding question 2 choices: 
            
        question2_id = cursor.execute("SELECT question_id FROM questions WHERE topic = ? AND text = ?", (topic,questions[1])).fetchone()[0]
        question2_choices = [request.form['correct_choice2'], request.form['choice2_2'], request.form['choice3_2'], request.form['choice4_2']]

        for i in range(len(question2_choices)):
            if i == 0:
                conn.execute("INSERT OR IGNORE INTO choices (question_id, choice_id, choice_text, correct) VALUES (?, ?, ?, ?)", (question2_id, i+1, question2_choices[i], 1))
                conn.commit()
            else:
                conn.execute("INSERT OR IGNORE INTO choices (question_id, choice_id, choice_text, correct) VALUES (?, ?, ?, ?)", (question2_id, i+1, question2_choices[i], 0))
                conn.commit()

        #Adding question 3 choices: 
                
        question3_id = cursor.execute("SELECT question_id FROM questions WHERE topic = ? AND text = ?", (topic,questions[2])).fetchone()[0]
        question3_choices = [request.form['correct_choice3'], request.form['choice2_3'], request.form['choice3_3'], request.form['choice4_3']]

        for i in range(len(question3_choices)):
            if i == 0:
                conn.execute("INSERT OR IGNORE INTO choices (question_id, choice_id, choice_text, correct) VALUES (?, ?, ?, ?)", (question3_id, i+1, question3_choices[i], 1))
                conn.commit()
            else:
                conn.execute("INSERT OR IGNORE INTO choices (question_id, choice_id, choice_text, correct) VALUES (?, ?, ?, ?)", (question3_id, i+1, question3_choices[i], 0))
                conn.commit()

        conn.close()
        return redirect(url_for('dashboard'))
    
    else: 
        return render_template('teacher_add_quiz.html')


@app.route('/teacher_delete_quiz', methods=['GET', 'POST'])
def teacher_delete_quiz():

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    if request.method == 'POST':
        
        topic = request.form['quiz']

        question_ids = cursor.execute("SELECT question_id FROM questions WHERE topic = ?", (topic,)).fetchall()

        for question_id in question_ids: 
            cursor.execute("DELETE FROM choices WHERE question_id = ?", (question_id[0],))
            cursor.execute("DELETE FROM student_choices WHERE question_id = ?", (question_id[0],))
            conn.commit()

        cursor.execute("DELETE FROM questions WHERE topic = ?", (topic,))
        conn.commit()


        conn.close()

        # Redirect to the same page with the deletion status flag
        return redirect(url_for('dashboard'))
    
    else: 

        topics = conn.execute("SELECT DISTINCT topic FROM questions").fetchall()
        conn.close()

        topic_list = []
        for i in topics: 
            topic_list.append(i[0])
        
        return render_template('teacher_delete_quiz.html', topics=topic_list)



# DEBUGGING  

    
@app.route('/view_students')
def view_students():
    conn = sqlite3.connect('database.db')
    students = conn.execute("SELECT * FROM students").fetchall()
    conn.close()

    return render_template('view_students.html', students=students)

@app.route('/view_questions')
def view_questions():

    conn = sqlite3.connect('database.db')
    questions = conn.execute("SELECT * FROM questions").fetchall()
    conn.close()
    return render_template('view_questions.html', questions=questions)


@app.route('/view_choices')
def view_choices():
    conn = sqlite3.connect('database.db')
    students = conn.execute("SELECT * FROM choices").fetchall()
    conn.close()
    return render_template('view_choices.html', students=students)


@app.route('/view_student_choices')
def view_student_choices():
    conn = sqlite3.connect('database.db')
    students = conn.execute("SELECT * FROM student_choices").fetchall()
    conn.close()
    return render_template('view_student_choices.html', students=students)

@app.route('/view_teachers')
def view_teachers():
    conn = sqlite3.connect('database.db')
    teachers = conn.execute("SELECT * FROM teachers").fetchall()
    conn.close()
    return render_template('view_teachers.html', teachers=teachers)

if __name__ == '__main__':
    app.run(debug=True)
