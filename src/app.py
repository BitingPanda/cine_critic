from flask import Flask, render_template
import sqlite3
import os

# Get the project root directory
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__,
            template_folder=os.path.join(os.path.dirname(__file__), '..', 'templates'),
            static_folder=os.path.join(project_root,'static'))

DATABASE = os.path.join(os.path.dirname(__file__),'..', 'databases','imdb.db')

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def home():
    conn = get_db_connection()
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
