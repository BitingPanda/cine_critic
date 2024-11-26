from flask import Flask, render_template, request
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

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('search', '').strip()

    # Redirect to home if query is empty
    if not query:
        return render_template('index.html')

    conn = get_db_connection()
    cursor = conn.cursor()

    # Dictionary to store search results
    search_results = {
            'titles': [],     # Movies or TV show titles
            'people': []
            }

    # Search in Titles
    cursor.execute("""
                   SELECT primary_title, original_title
                   FROM titles
                   WHERE primary_title LIKE ? OR original_title LIKE ?
                   ORDER BY primary_title
                   LIMIT 10
                   """, (f'%{query}%', f'%{query}%'))
    search_results['titles'] = cursor.fetchall()

    # Search for Actors in People Table
    cursor.execute("""
                   SELECT name, born, died
                   FROM people
                   WHERE name LIKE ?
                   ORDER BY name 
                   LIMIT 10
                   """, (f'%{query}%',))
    search_results['people'] = cursor.fetchall()

    # Search for Directors in Crew Table
    # cursor.execute("""
    #                SELECT p.name, p.birth_year, p.death_year
    #                FROM crew c
    #                JOIN people p ON c.directors = p.id
    #                WHERE p.name LIKE ?
    #                ORDER BY p.name
    #                LIMIT 10
    #                """, (f'%{query}%',))
    # search_results['directors'] = cursor.fetchall()

    conn.close()

    # Render results page
    return render_template(
            'search_results.html',
            results=search_results,
            query=query
            )



if __name__ == '__main__':
    app.run(debug=True)
