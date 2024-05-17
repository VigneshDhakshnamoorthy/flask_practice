import sqlite3
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Function to establish database connection
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# Initialize database
def init_database():
    conn = get_db_connection()
    conn.execute('CREATE TABLE IF NOT EXISTS utilizationbytask (id INTEGER PRIMARY KEY AUTOINCREMENT, task TEXT, hours INTEGER)')
    conn.close()

# Initialize the database when the application starts
init_database()

@app.route('/', methods=['GET', 'POST'])
def index():
    conn = get_db_connection()
    if request.method == 'POST':
        # Handle updates to the database
        updated_data = request.json['data']
        for row in updated_data:
            task_id = row['id']
            task = row['task']
            hours = row['hours']
            conn.execute('UPDATE utilizationbytask SET task = ?, hours = ? WHERE id = ?', (task, hours, task_id))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Data updated successfully'})
    # Fetch data from the database
    cursor = conn.execute('SELECT id, task, hours FROM utilizationbytask')
    data = cursor.fetchall()
    conn.close()
    return render_template('index2.html', data=data)

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=6967, threaded=True)
