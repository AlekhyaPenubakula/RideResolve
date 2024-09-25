from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Connect to MySQL RDS instance
db_config = {
    'user': 'admin',
    'password': 'database-1_rds',
    'host': 'database-1.cfomkoee8n2n.ap-south-1.rds.amazonaws.com',
    'database': 'transport'
}
conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()

# Home Route (Login Page)
@app.route('/')
def index():
    return render_template('index.html')

# Registration Page
@app.route('/register')
def register():
    return render_template('register.html')

# Register User
@app.route('/register', methods=['POST'])
def register_user():
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    confirm_password = request.form['confirm_password']

    if password != confirm_password:
        error_message = "Passwords do not match. Please try again."
        return render_template('register.html', error=error_message)

    hashed_password = generate_password_hash(password)
    login_count = 0
    
    cursor.execute("INSERT INTO users (email, username, password, login_count) VALUES (%s, %s, %s, %s)",
                   (email, username, hashed_password, login_count))
    conn.commit()
    
    return redirect(url_for('index'))


# Login Route
@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')

    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()

    if user and check_password_hash(user[3], password):
        # Update login count
        new_login_count = user[4] + 1
        cursor.execute("UPDATE users SET login_count = %s WHERE email = %s", (new_login_count, email))
        conn.commit()

        # Redirect to dashboard with the username as a query parameter
        return redirect(url_for('dashboard', username=user[2]))
    else:
        error_message = "Incorrect password. Please try again."
        return render_template('index.html', error=error_message)  # Pass error message

# User Dashboard (Personalized with Username)
@app.route('/dashboard')
def dashboard():
    username = request.args.get('username')
    return render_template('dashboard.html', username=username)


# Schedule Page
@app.route('/schedule')
def schedule():
    return render_template('schedule.html')

# Complaint Form
@app.route('/complaint')
def complaint():
    return render_template('complaint.html')

# Submit a complaint
@app.route('/submit_complaint', methods=['POST'])
def submit_complaint():
    # Get form data
    vehicle_type = request.form.get('vehicle_type')
    route_no = request.form.get('route_no')
    vehicle_no = request.form.get('vehicle_no')
    query_type = request.form.get('query_type')
    description = request.form.get('description')

    # Validate the form inputs (optional)
    if not all([vehicle_type, route_no, vehicle_no, query_type, description]):
        return "All fields are required", 400

    # Insert the data into MySQL database
    try:
        cursor.execute("INSERT INTO complaints (vehicle_type, route_no, vehicle_no, query_type, description) VALUES (%s, %s, %s, %s, %s)",
                       (vehicle_type, route_no, vehicle_no, query_type, description))
        conn.commit()
        return " Thank you for your query. We will check on it."
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return "There was an issue submitting your complaint", 500


if __name__ == '__main__':
    app.run(debug=True)
