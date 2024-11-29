from flask import Flask, render_template, request, url_for, redirect
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
        'titles': [],  # Movies or TV show titles
    }

    # Use FTS5 for Titles Search
    cursor.execute("""
        SELECT title_id, primary_title, original_title
        FROM search_index
        WHERE search_index MATCH ?
        LIMIT 10
    """, (query,))
    search_results['titles'] = cursor.fetchall()

    conn.close()

    # Render results page
    return render_template(
        'search_results.html',
        results=search_results,
        query=query
    )


@app.route('/movie/<title_id>', methods=['GET', 'POST'])
def movie_detail(title_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch movie details using the title_id
    cursor.execute("SELECT * FROM titles WHERE title_id = ?", (title_id,))
    movie = cursor.fetchone()

    # Fetch reviews for this movie
    cursor.execute("SELECT * FROM reviews WHERE title_id = ?", (title_id,))
    reviews = cursor.fetchall()

    if request.method == 'POST':
        # Handle the form submission for adding a new review
        reviewer_name = request.form['reviewer_name']
        review_text = request.form['review_text']

        # Insert the new review into the reviews table
        cursor.execute("""
            INSERT INTO reviews (title_id, reviewer_name, review_text)
            VALUES (?, ?, ?)
        """, (title_id, reviewer_name, review_text))

        # Commit the changes
        conn.commit()

        # Redirect back to the movie detail page to see the new review
        return redirect(url_for('movie_detail', title_id=title_id))

    conn.close()

    return render_template('movie_detail.html', movie=movie, reviews=reviews)








if __name__ == '__main__':
    app.run(debug=True)
