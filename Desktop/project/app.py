from flask import Flask, json, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import sqlite3
import os
import random
from flask_mail import Mail, Message
import mysql.connector
import subprocess
import requests
from dotenv import load_dotenv
from flask_cors import CORS
app = Flask(__name__)
CORS(app)
app.secret_key = 'supersecretkey'
load_dotenv()
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Configure Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'priyankapri425@gmail.com'
app.config['MAIL_PASSWORD'] = 'vyce qukn sqts zugn'
app.config['MAIL_DEFAULT_SENDER'] = 'ATAP@gmail.com'
mail = Mail(app)

otp_storage = {}




# MySQL Configuration
mysql_config = {
    'host': 'localhost',
    'database': 'project_db',
    'user': 'root',
    'password': 'Priya@2003'
}

# Database connection
def get_db_connection():
    try:
        conn = mysql.connector.connect(**mysql_config)
        if conn.is_connected():
            return conn
        else:
            print("Failed to connect to the database.")
            return None
    except mysql.connector.Error as err:
        print(f"Database connection error: {err}")
        return None

# Helper functions
def execute_query(query, params=None):
    conn = get_db_connection()
    if not conn:
        print("Connection error, query cannot be executed.")
        return None
    cursor = conn.cursor()
    try:
        cursor.execute(query, params or ())
        conn.commit()
        return cursor.fetchall() if cursor.with_rows else None
    except mysql.connector.Error as err:
        print(f"Error executing query: {err}")
        return None
    finally:
        cursor.close()
        conn.close()
@app.route('/code_correctness', methods=['GET', 'POST'])
def code_correctness():
    if 'user_id' not in session:
        flash('Please log in to access this page.')
        return redirect(url_for('login'))

    corrected_code_result = None  # Default value if no code is submitted

    if request.method == 'POST':
        # Get the input code from the form
        input_code = request.form.get('input_code')

        # Call the Gemini API
        api_url = 'https://api.gemini.com/v1/correct_code'  # Replace with the actual Gemini API endpoint
        headers = {
            'Authorization': f'Bearer {GEMINI_API_KEY}',
            'Content-Type': 'application/json'
        }
        payload = {'input_code': input_code}

        response = requests.post(api_url, headers=headers, json=payload)

        if response.status_code == 200:
            corrected_code_result = response.json().get('corrected_code', '')
        else:
            corrected_code_result = "Error correcting code. Please try again later."

    return render_template('code_correctness.html', corrected_code=corrected_code_result)

def safe_execute(code):
    try:
        process = subprocess.run(
            ['python3', '-c', code],
            capture_output=True,
            text=True,
            timeout=5
        )
        return process.stdout if process.returncode == 0 else process.stderr
    except subprocess.TimeoutExpired:
        return "Execution timed out."



def seed_db():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            hashed_password = generate_password_hash("admin123")
            cursor.execute('''
                INSERT IGNORE INTO users (username, email, password)
                VALUES (%s, %s, %s)
            ''', ('admin', 'admin@example.com', hashed_password))

            users = [
                ]
            cursor.executemany('''
                INSERT IGNORE INTO users (username, email, password)
                VALUES (%s, %s, %s)
            ''', users)
            conn.commit()
            print("Seed data added successfully.")
        except mysql.connector.Error as err:
            print(f"Error seeding database: {err}")
        finally:
            cursor.close()
            conn.close()
    else:
        print("Database connection failed during seeding.")




conn = get_db_connection()
if conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    results = cursor.fetchall()
    cursor.close()
    conn.close()
else:
    print("Connection failed, cannot create cursor.")

# Add admin user
admin_email = "admin@example.com"
admin_password = "admin123"
hashed_password = generate_password_hash(admin_password)

import logging
logging.basicConfig(level=logging.DEBUG)
import json  # Ensure you import Python's built-in json module

@app.route('/add_problem', methods=['POST'])
def add_problem():
    data = request.get_json()
    logging.debug(f"Received data: {data}")

    title = data.get('title')
    description = data.get('description')
    test_cases = data.get('testCases')
    topic = data.get('topic')

    # Validate that all fields are provided
    if not (title and description and test_cases and topic):
        logging.error("Missing required fields")
        return jsonify({'error': 'All fields are required'}), 400

    # Validate and parse JSON format for test cases
    try:
        test_cases = json.loads(test_cases)
    except ValueError as e:  # Use ValueError instead of JSONDecodeError
        logging.error(f"Invalid JSON format: {e}")
        return jsonify({'error': 'Invalid JSON format for test cases'}), 400

    # Connect to the database
    conn = get_db_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            # Insert data into the database
            cursor.execute(
                'INSERT INTO problems (title, description, test_cases, topic) VALUES (%s, %s, %s, %s)',
                (title, description, json.dumps(test_cases), topic)
            )
            conn.commit()
            conn.close()
            return jsonify({'success': 'Problem added successfully'}), 200
        except Exception as e:
            logging.error(f"Database error: {e}")
            conn.close()
            return jsonify({'error': f'Database error: {e}'}), 500
    else:
        logging.error("Database connection error")
        return jsonify({'error': 'Database connection error'}), 500
    
@app.route('/admin_dashboard')
def admin_dashboard():
    if 'user_id' not in session or not session.get('is_admin'):
        flash('Access denied. Admins only.')
        return redirect(url_for('login'))
    return render_template('admin_dashboard.html')

# Initialize MySQL tables
def create_table():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(255) UNIQUE,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    college TEXT,
                    phone_number TEXT,
                    profile_photo TEXT
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS problems (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    title VARCHAR(255) NOT NULL,
                    description TEXT NOT NULL,
                    test_cases JSON NOT NULL
                )
            ''')
            conn.commit()
            print("Tables created successfully.")
        except mysql.connector.Error as err:
            print(f"Error creating tables: {err}")
        finally:
            cursor.close()
            conn.close()
    else:
        print("Could not establish database connection.")


@app.route('/')
def splash():
    return render_template('splash.html')

@app.route('/Home')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')




def send_email(to_email, subject, message):
    try:
        msg = Message(subject=subject,
                      recipients=[to_email],
                      body=message)
        mail.send(msg)
    except Exception as e:
        print(f"Failed to send email: {e}")
        flash(f"Failed to send email: {e}")

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']

        # Create the email
        msg = Message('New Contact Form Message',
                      sender=email,
                      recipients=['priyankapri425@gmail.com'])
        msg.body = f"Name: {name}\nEmail: {email}\nMessage:\n{message}"

        # Send the email
        mail.send(msg)

        flash('Your message has been sent successfully!')
        return redirect(url_for('contact'))
    return render_template('contact.html')



BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')  # Directory for storing profile photos
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']



# Route to view and update the profile
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        flash('Please log in to access this page.')
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)  # Use dictionary cursor for fetching results as a dictionary
    cursor.execute('SELECT * FROM users WHERE id = %s', (session['user_id'],))
    user = cursor.fetchone()

    if request.method == 'POST':
        college = request.form.get('college', '')
        phone_number = request.form.get('phone_number', '')

        # Handle profile photo upload
        profile_photo = request.files.get('profile_photo')
        if profile_photo and allowed_file(profile_photo.filename):
            filename = secure_filename(profile_photo.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            profile_photo.save(file_path)
            profile_photo_path = filename
        else:
            profile_photo_path = user['profile_photo']  # Use existing profile photo if no new one is uploaded

        # Update user details in the database
        cursor.execute('''
            UPDATE users
            SET college = %s, phone_number = %s, profile_photo = %s
            WHERE id = %s
        ''', (college, phone_number, profile_photo_path, session['user_id']))
        conn.commit()
        flash('Profile updated successfully!')
        return redirect(url_for('profile'))

    cursor.close()
    conn.close()
    return render_template('profile.html', user=user)

# Route to update only profile photo
@app.route('/update_profile_photo', methods=['POST'])
def update_profile_photo():
    if 'user_id' not in session:
        flash('Please log in to access this page.')
        return redirect(url_for('login'))

    file = request.files.get('profile_photo')
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET profile_photo = %s WHERE id = %s', (filename, session['user_id']))
        conn.commit()
        cursor.close()
        conn.close()

        flash('Profile photo updated successfully!')
    else:
        flash('Invalid file format or no file uploaded.')
    return redirect(url_for('profile'))

@app.route('/update_profile_details', methods=['POST'])
def update_profile_details():
    if 'user_id' not in session:
        flash('Please log in to access this page.')
        return redirect(url_for('login'))
    
    college = request.form['college']
    phone_number = request.form['phone_number']
    
    conn = get_db_connection()
    conn.execute('UPDATE users SET college = ?, phone_number = ? WHERE id = ?', (college, phone_number, session['user_id']))
    conn.commit()
    conn.close()
    
    flash('Profile details updated successfully!')
    return redirect(url_for('profile'))

# @app.route('/upload', methods=['POST'])
# def upload_profile_photo():
#     if 'profile_photo' in request.files:
#         file = request.files['profile_photo']
#         filename = secure_filename(file.filename)
#         file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
#         # Save the filename in the database (example: 'Snapchat-674217206.jpg')
#         user.profile_photo = filename
#         db.session.commit()
#         return redirect(url_for('profile'))
    
# @app.route('/update', methods=['POST'])
# def update_profile_photo():
#     if 'user_id' not in session:
#         flash('Please log in to access this page.')
#         return redirect(url_for('login'))
    
#     file = request.files.get('profile_photo')
#     if file and allowed_file(file.filename):
#         filename = secure_filename(file.filename)
#         file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
#         conn = get_db_connection()
        
#         # Check if user details exist for the user, if not, insert them
#         conn.execute('INSERT OR REPLACE INTO users (user_id, profile_photo) VALUES (%s, %s)',
#                      (session['user_id'], filename))
#         conn.commit()
#         conn.close()
#         flash('Profile photo updated successfully!')
#     else:
#         flash('Invalid file format or no file uploaded.')
#     return redirect(url_for('profile'))

# @app.route('/update_profile_details', methods=['POST'])
# def update_profile_details():
#     if 'user_id' not in session:
#         flash('Please log in to access this page.')
#         return redirect(url_for('login'))
    
#     college = request.form['college']
#     phone_number = request.form['phone_number']
    
#     # Connect to SQLite database and update profile details
#     conn = get_db_connection()
#     conn.execute('UPDATE users SET college = %s, phone_number = %s WHERE id = %s', (college, phone_number, session['user_id']))
#     conn.commit()
#     conn.close()
    
#     flash('Profile details updated successfully!')
#     return redirect(url_for('profile'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.')
    return redirect(url_for('index'))

def send_otp(to_email, otp):
    try:
        msg = Message(subject='Your OTP',
                      recipients=[to_email],
                      body=f'Your OTP is {otp}')
        mail.send(msg)
        print(f"OTP sent: {otp}")  # Debug print
    except Exception as e:
        print(f"Failed to send email: {e}")
        flash(f"Failed to send email: {e}")

@app.route('/send_otp', methods=['POST'])
def send_otp():
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    confirm_password = request.form['confirm_password']

    if password != confirm_password:
        return jsonify({'success': False, 'message': 'Passwords do not match!'})

    # Generate OTP
    otp = random.randint(100000, 999999)
    session['otp'] = otp
    session['username'] = username
    session['email'] = email
    session['password'] = password

    print(f"Generated OTP: {otp}")  # Debug print

    # Send OTP to email
    send_email(email, 'Your OTP', f'Your OTP is {otp}')

    return jsonify({'success': True, 'message': 'OTP sent to your email!'})


# Additional routes for signup, login, profile, etc., using MySQL queries
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash('Passwords do not match!')
            return redirect(url_for('signup'))

        hashed_password = generate_password_hash(password)
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    'INSERT INTO users (username, email, password) VALUES (%s, %s, %s)',
                    (username, email, hashed_password)
                )
                conn.commit()
                flash('Signup successful!')
                return redirect(url_for('login'))
            except mysql.connector.IntegrityError as e:
                if "Duplicate entry" in str(e):
                    flash('Username or email already exists!')
                else:
                    flash('An error occurred during signup.')
            finally:
                cursor.close()
                conn.close()
        else:
            flash('Database connection error.')
    return render_template('signup.html')


@app.route('/verify_otp', methods=['POST'])
def verify_otp():
    if request.is_json:
        otp_input = request.json.get('otp')
    else:
        otp_input = request.form.get('otp')

    stored_otp = session.get('otp')

    if otp_input is None:
        return jsonify({'success': False, 'message': 'No OTP provided!'})

    if stored_otp is not None and int(otp_input) == int(stored_otp):
        username = session.pop('username', None)
        email = session.pop('email', None)
        password = session.pop('password', None)

        if not all([username, email, password]):
            return jsonify({'success': False, 'message': 'Session data is missing!'})

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        conn = get_db_connection()
        if conn:
            curr = conn.cursor()
            try:
                curr.execute(
                    'INSERT INTO users (username, email, password) VALUES (%s, %s, %s)',
                    (username, email, hashed_password)
                )
                conn.commit()
                session.pop('otp', None)  # Clear OTP after successful verification
                return jsonify({'success': True, 'message': 'Sign up successful!'})
            except mysql.connector.IntegrityError:
                return jsonify({'success': False, 'message': 'Username or email already exists!'})
            finally:
                curr.close()
                conn.close()
        else:
            return jsonify({'success': False, 'message': 'Database connection error!'})
    else:
        return jsonify({'success': False, 'message': 'Invalid OTP!'})
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Check if admin credentials are used
        if email == 'admin@example.com' and password == 'admin123':
            session['user_id'] = 'admin'
            session['is_admin'] = True
            flash('Welcome, Admin!')
            return redirect(url_for('admin_dashboard'))

        # Check database for regular user credentials
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor(dictionary=True)  # Use dictionary cursor for easier access
                cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
                user = cursor.fetchone()  # Fetch the first matching user (consumes the result)

                if user and check_password_hash(user['password'], password):
                    session['user_id'] = user['id']
                    session['is_admin'] = False
                    flash('Login successful!')
                    return redirect(url_for('index'))
                else:
                    flash('Invalid email or password!')
                    return redirect(url_for('login'))
            except Exception as e:
                flash(f"Error: {str(e)}")
                return redirect(url_for('login'))
            finally:
                # Always close the cursor and connection
                cursor.close()
                conn.close()
        else:
            flash('Database connection error.')
            return render_template('login.html')

    return render_template('login.html')

# @app.route('/problem_solving')
# def problem_solving():
#     if 'user_id' not in session:
#         flash('Please log in to access this page.')
#         return redirect(url_for('login'))
#     return render_template('problem_solving.html')

@app.route('/get_questions')
def get_questions():
    language = request.args.get('language')
    questions = {
    "python": [{"number": 1, "type": "loops", "time_taken": "10 min", "score": 10, "status": "unsolved"}],}
    return jsonify(questions.get(language, []))

@app.route('/run_code', methods=['POST'])
def run_code():
    data = request.json
    code = data['code']
    input_data = data['input']
    # Code execution logic here
    output = f"Executed code: {code} with input {input_data}"
    return jsonify({"output": output})

@app.route('/submit_code', methods=['POST'])
def submit_code():
    data = request.json
    code = data['code']
    # Submission logic here
    return jsonify({"message": "Code submitted successfully!"})

@app.route('/question_selector', methods=['GET'])
def question_selector():
    if 'user_id' not in session:
        flash('Please log in to access this page.')
        return redirect(url_for('login'))
    conn = get_db_connection()
    cursor = conn.cursor()
    topic = request.args.get('topic')

    # Log the topic for debugging
    logging.debug(f"Fetching problems for topic: {topic}")

    # Fetch only titles and IDs for the selected topic
    query = "SELECT id, title FROM problems WHERE topic = %s"
    cursor.execute(query, (topic,))
    problems = cursor.fetchall()

    # Log the result of the query
    logging.debug(f"Fetched problems: {problems}")

    # Check if problems are retrieved
    if not problems:
        logging.warning(f"No problems found for topic: {topic}")

    # Create a default "unsolved" status for all problems
    questions = [{"id": p[0], "title": p[1], "status": "unsolved"} for p in problems]

    # Pass questions to the template
    return render_template("question_selector.html", questions=questions)

@app.route('/coding_environment/<int:question_id>', methods=['GET', 'POST'])
def coding_environment(question_id):
    # Retrieve the problem details from the database using question_id
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM problems WHERE id = %s"
    cursor.execute(query, (question_id,))
    p = cursor.fetchone()

    if p:
        print(p)  # Print the problem to check its contents
        return render_template("coding_environment.html", problem=p)

    else:
        return jsonify({"error": "Problem not found"}), 404



@app.route('/game')
def game():
    if 'user_id' not in session:
        flash('Please log in to access this page.')
        return redirect(url_for('login'))
    return render_template('game.html')@app.route('/execute_code', methods=['POST'])

import re

def sanitize_function_name(title):
    # Replace invalid characters with underscores and ensure it starts with a valid identifier
    return re.sub(r'\W|^(?=\d)', '_', title)
@app.route('/execute_code', methods=['POST'])
def execute_code():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON data"}), 400

        code = data.get("code", "")
        language = data.get("language", "python")
        problem_id = data.get("problemId", None)

        if not problem_id:
            return jsonify({"error": "Problem ID is required"}), 400

        if language != "python":
            return jsonify({"error": "Only Python is supported."}), 400

        # Fetch problem details from the database
        try:
            db_connection = get_db_connection()
            cursor = db_connection.cursor(dictionary=True)

            cursor.execute("SELECT * FROM problems WHERE id = %s", (problem_id,))
            problem = cursor.fetchone()

            if not problem:
                return jsonify({"error": f"Problem with ID {problem_id} not found"}), 404

            # Extract test cases and sanitize the title as the function name
            test_cases = json.loads(problem['test_cases'])
            raw_function_name = problem['title']
            function_name = sanitize_function_name(raw_function_name)
            results = []

            try:
                # Execute user-provided code
                exec_globals = {}
                exec(code, exec_globals)

                # Fallback to find any user-defined function if the expected one is not found
                if function_name not in exec_globals:
                    user_defined_functions = [
                        name for name, obj in exec_globals.items() if callable(obj)
                    ]
                    if not user_defined_functions:
                        return jsonify({
                            "error": f"No function found in the provided code. "
                                     f"Expected: '{raw_function_name}' (sanitized as '{function_name}')."
                        }), 400
                    elif len(user_defined_functions) > 1:
                        return jsonify({
                            "error": f"Multiple functions found in the provided code. "
                                     f"Expected: '{raw_function_name}' (sanitized as '{function_name}')."
                        }), 400
                    else:
                        # Use the only available function as fallback
                        function_name = user_defined_functions[0]

                user_function = exec_globals[function_name]

                for test_case in test_cases:
                    test_input = test_case['input']
                    expected_output = test_case['output']

                    try:
                        if isinstance(test_input, list):
                            actual_output = user_function(*test_input)
                        else:
                            actual_output = user_function(test_input)

                        passed = (str(actual_output) == str(expected_output))
                        results.append({
                            "test_case_id": test_case.get("id", len(results) + 1),
                            "input": test_input,
                            "expected_output": expected_output,
                            "actual_output": actual_output,
                            "passed": passed
                        })

                    except Exception as e:
                        results.append({
                            "test_case_id": test_case.get("id", len(results) + 1),
                            "input": test_input,
                            "expected_output": expected_output,
                            "actual_output": str(e),
                            "passed": False
                        })

            except Exception as e:
                return jsonify({"error": f"Code execution failed: {e}"}), 400

            return jsonify({"results": results})

        except mysql.connector.Error as err:
            return jsonify({"error": f"Database error: {err}"}), 500

        finally:
            if 'db_connection' in locals():
                db_connection.close()

    except Exception as e:
        return jsonify({"error": f"Unexpected server error: {e}"}), 500
# @app.route('/test_db')
# def test_db():
#     try:
#         cursor = conn.cursor()
#         cursor.execute("SHOW TABLES;")
#         tables = cursor.fetchall()
#         return jsonify({"tables": tables})
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500
    
if __name__ == '__main__':
    create_table()
    seed_db()
    app.run(debug=True)