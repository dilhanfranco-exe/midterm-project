from flask import Flask, abort, render_template, request, redirect, url_for, session, jsonify
import pymysql
from flask_cors import CORS
import re
import os
import jwt
from werkzeug.utils import secure_filename
from functools import wraps
from datetime import datetime, timedelta
import json

# activate the virtual environment
#. venv/bin/activate 

app = Flask(__name__)

app.config['SECRET_KEY'] = 'cba48681230f44d2a67477fffec7bf44' # Randomly generated secret key from uuid approach
# CORS(app)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

#data that is open to the public
results = [
	{"user": 1, "name": "Bazinga"},
	{"user": 2, "name": "Rhi Rhi"},
	{"user": 3, "name": "The Rock"}
]

conn = pymysql.connect(
        host='localhost',
        user='root', 
        password = "1234567890", 
        db='midterm_project',
		cursorclass=pymysql.cursors.DictCursor
        )
cur = conn.cursor()

# activate the virtual environment
#. venv/bin/activate 

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024
app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.png', '.gif']
app.config['UPLOAD_PATH'] = 'uploads'
UPLOAD_FOLDER = '/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER 

# decorator for token authentication
def token_required(func):
	@wraps(func)
	def decorated(*args, **kwargs):
		token = request.args.get('token')
		if not token:
			return jsonify({'Alert!': 'Token is missing!'}), 401
		try:
			data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])

		except:
			return jsonify({'Alert!': 'Invalid token'}), 403
		return func(*args, **kwargs)
	return decorated

@app.route('/')
@app.route('/public')
def public():
	return render_template('public.html', results=results)


@app.route('/login', methods =['GET', 'POST'])
def login():
	msg = ''
	if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
		#code from video reference to make the session permanent
		username = request.form['username']
		password = request.form['password']
		cur.execute('SELECT * FROM accounts WHERE username = % s AND password = % s', (username, password, ))
		conn.commit()
		account = cur.fetchone()

		if account:
            
			session['loggedin'] = True
			session['id'] = account['id']
			session['username'] = account['username']
			msg = 'Logged In Successfully.'
			# uses jwt to generate a token
			token = jwt.encode({
				'user': request.form['username'],
				'expiration': str(datetime.utcnow() + timedelta(seconds=60))
			},app.config['SECRET_KEY'])
			session['token'] = token
			return redirect(url_for('index', token = token))

		else:
			msg = 'Invalid Credentials. Please Try Again.'
			return render_template('login.html', msg = msg)

	else:
		return render_template('login.html', msg = msg)

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/register', methods =['GET', 'POST'])
def register():
	msg = ''
	if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
		print('reached')
		username = request.form['username']
		password = request.form['password']
		email = request.form['email']

		cur.execute('SELECT * FROM accounts WHERE username = % s', (username))
		account = cur.fetchone()
		print(account)
		conn.commit()

		if account:
			msg = 'Account already exists.'
		elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
			msg = 'Invalid email address.'
		elif not re.match(r'[A-Za-z0-9]+', username):
			msg = 'name must contain only characters and numbers.'
		else:
			cur.execute('INSERT INTO accounts VALUES (NULL, % s, % s, % s)', (username, password, email))
			conn.commit()

			msg = 'Registered Successfully.'
	elif request.method == 'POST':
		msg = 'Incomplete Form.'
	return render_template('register.html', msg = msg)

@app.route("/index")
@token_required
def index():
	if 'loggedin' in session:
		return render_template("index.html")
	return redirect(url_for('login'))

@app.route('/success', methods=['POST'])
def upload_files():
    uploaded_file = request.files['file']
    filename = secure_filename(uploaded_file.filename)
    if filename != '':
        file_ext = os.path.splitext(filename)[1]
        if file_ext not in app.config['UPLOAD_EXTENSIONS']:
            abort(415)
        
        uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], filename))
        return render_template('successful.html')


@app.route("/admin")
@token_required
def admin():
	# if the session username isn't "admin"
	if session['username'] != 'admin':
		#then the program will throw the error 401
		abort(401)
	else:
		#if the user name is "admin" then it will render the template admin.html
		return render_template("admin.html")


#Error Handling Code
@app.errorhandler(400)
def bad_request(e):
    return render_template('400.html'), 400

@app.errorhandler(401)
def unauthorized(e):
    return render_template('401.html'), 401

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(413)
def content_too_large(e):
    return render_template('413.html'), 413

@app.errorhandler(415)
def unsupported_media(e):
    return render_template('415.html'), 415

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500



if __name__ == "__main__":
    app.secret_key = os.urandom(24)
app.run(host ="localhost", port = int("3308"))
