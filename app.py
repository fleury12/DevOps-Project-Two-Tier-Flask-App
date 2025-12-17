import os
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_mysqldb import MySQL

try:
    from elasticapm.contrib.flask import ElasticAPM
except ImportError:
    ElasticAPM = None

app = Flask(__name__)

if os.environ.get('ELASTIC_APM_SERVER_URL') and ElasticAPM is not None:
    def _parse_bool(value: str, default: bool = True) -> bool:
        if value is None:
            return default
        return value.strip().lower() in {'1', 'true', 'yes', 'y', 'on'}

    app.config['ELASTIC_APM'] = {
        'SERVICE_NAME': os.environ.get('ELASTIC_APM_SERVICE_NAME', 'flask-app'),
        'SERVER_URL': os.environ['ELASTIC_APM_SERVER_URL'],
        'SECRET_TOKEN': os.environ.get('ELASTIC_APM_SECRET_TOKEN', ''),
        'ENVIRONMENT': os.environ.get('ELASTIC_APM_ENVIRONMENT', 'dev'),
        'VERIFY_SERVER_CERT': _parse_bool(os.environ.get('ELASTIC_APM_VERIFY_SERVER_CERT', 'true'), default=True),
    }
    apm = ElasticAPM(app)

# Configure MySQL from environment variables
app.config['MYSQL_HOST'] = os.environ.get('MYSQL_HOST', 'localhost')
app.config['MYSQL_USER'] = os.environ.get('MYSQL_USER', 'default_user')
app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD', 'default_password')
app.config['MYSQL_DB'] = os.environ.get('MYSQL_DB', 'default_db')

# Initialize MySQL
mysql = MySQL(app)

def init_db():
    with app.app_context():
        cur = mysql.connection.cursor()
        cur.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INT AUTO_INCREMENT PRIMARY KEY,
            message TEXT
        );
        ''')
        mysql.connection.commit()  
        cur.close()

@app.route('/')
def hello():
    cur = mysql.connection.cursor()
    cur.execute('SELECT message FROM messages')
    messages = cur.fetchall()
    cur.close()
    return render_template('index.html', messages=messages)

@app.route('/submit', methods=['POST'])
def submit():
    new_message = request.form.get('new_message')
    cur = mysql.connection.cursor()
    cur.execute('INSERT INTO messages (message) VALUES (%s)', [new_message])
    mysql.connection.commit()
    cur.close()
    return jsonify({'message': new_message})

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)