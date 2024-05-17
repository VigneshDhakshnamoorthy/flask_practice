import sqlite3
from flask import Flask, render_template, request, jsonify, session

app = Flask(__name__)
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'

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
    project_select: str | None = None
    week_select: str | None = None
    project_list: list =  ["Project1", "Project2"]
    week_list: list =  ["Week1", "Week2"]
    if request.method == 'GET':
        session["select_project"] = project_list[0]
        project_select = project_list[0]
        week_select = week_list[0]

    if request.method == "POST" and "select_project" in request.form:
        project_select = request.form.get("select_project")
        session["select_project"] = project_select
        week_select:str = session["select_week"]
        return jsonify({'message': f'{project_select} & {week_select} Selected'})

    if request.method == "POST" and "select_week" in request.form:
        week_select = request.form.get("select_week")
        session["select_week"] = week_select
        project_select:str = session["select_project"]
        return jsonify({'message': f'{project_select} & {week_select} Selected'})
         
    print(f"Project : {project_select} Week : {week_select}")
    conn = get_db_connection()
    project_select = "Project1"
    week_select = "Week1"
    if request.method == 'POST'and 'data' in request.json:
        project_select:str = session["select_project"]
        week_select:str = session["select_week"]
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
    cursor = conn.execute('SELECT id, task, hours FROM utilizationbytask WHERE project = ? AND week = ?', (project_select, week_select))
    data = cursor.fetchall()
    conn.close()
    return render_template('index2.html', data=data, project_list =project_list, week_list = week_list, selected_project = project_select, selected_week = week_select)

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=6967, threaded=True)
