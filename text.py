import sqlite3
from flask import Flask, request, render_template, redirect, url_for

app = Flask(__name__)
DB_NAME = 'your_database.db'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER NOT NULL,
            author TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM comments ORDER BY created_at DESC')
    comments = cursor.fetchall()
    conn.close()
    return render_template('text.html', comments=comments)

@app.route('/add_comment', methods=['POST'])
def add_comment():
    item_id = request.form.get('item_id', 1)  # 기본값 1로 설정
    author = request.form['author']
    content = request.form['content']
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO comments (item_id, author, content) VALUES (?, ?, ?)',
                   (item_id, author, content))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
