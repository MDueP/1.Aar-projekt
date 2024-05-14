import base64
from io import BytesIO
from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
from flask_mysqldb import MySQL
import MySQLdb.cursors
import MySQLdb.cursors, re
import matplotlib.pyplot as plt
import matplotlib
from flask_bcrypt import Bcrypt
matplotlib.use('agg')
app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key = 'mikkelersej'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'pythonlogin'

mysql = MySQL(app)
def graph():
    fig, axd = plt.subplot_mosaic([['upleft', 'right'],
                               ['lowleft', 'right']], layout='constrained')
    axd['upleft'].set_title('upleft')
    axd['lowleft'].set_title('lowleft')
    axd['right'].set_title('right')
    buf = BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    data = base64.b64encode(buf.getvalue()).decode("ascii")
    plt.close(fig)
    return data
    
@app.route('/', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM pythonlogin.accounts WHERE username = %s', (username,))
        account = cursor.fetchone()
        if account and bcrypt.check_password_hash(account['password'], password):
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            return redirect(url_for('home'))
        else:
            msg = 'Incorrect Username or Password'
    return render_template('index.html', msg=msg)

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM pythonlogin.accounts WHERE username = %s', (username,))
        account = cursor.fetchone()
        
        if account:
            msg = 'Account already exists'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = "Invalid email"
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers'
        elif not username or not password or not email:
            msg = 'Please fill out all the fields'
        else:
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            cursor.execute('INSERT INTO pythonlogin.accounts VALUES (NULL, %s, %s, %s)', (username, hashed_password, email,))
            mysql.connection.commit()
            msg = 'Successfully registered'
    elif request.method == 'POST':
        msg = 'Please fill out all the fields '
    return render_template('register.html', msg=msg)

@app.route('/home')
def home():
    Graph = graph()
    if 'loggedin' in session:
        return render_template('home.html', username=session['username'], Graph=Graph)
    return redirect(url_for('login'))
        
app.run(host="0.0.0.0", debug=True, ssl_context='adhoc')