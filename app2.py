import sqlite3
from typing import Any, List, LiteralString, Tuple
from database_helper import DatabaseHelper
from flask import Flask, Response, render_template, request, jsonify, session

app = Flask(__name__)
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'
db_name = './database/database.db'

db_helper = DatabaseHelper(db_name)

@app.route('/', methods=['GET', 'POST'])
def index() -> str:
    project_select: str | None = None
    week_select: str | None = None
    project_list: list =  ["Project1", "Project2"]
    week_list: list =  ["Week1", "Week2"]
    if request.method == 'GET':
        project_select = session["select_project"] if "select_project" in session else project_list[0]
        week_select = session["select_week"] if "select_week" in session else week_list[0]
        session["select_project"] = project_select
        session["select_week"] = week_select

    if request.method == "POST" and "select_project" in request.form:
        project_select = request.form.get("select_project")
        session["select_project"] = project_select
        week_select:str = session["select_week"]

    if request.method == "POST" and "select_week" in request.form:
        week_select = request.form.get("select_week")
        session["select_week"] = week_select
        project_select:str = session["select_project"]
    print(project_select, week_select)
    activity_this_week: List[Tuple[Any]] = db_helper.fetch_all('SELECT id, activity, count FROM activity_this_week WHERE project = ? AND week = ?', (project_select, week_select))
    activity_this_week_size: int = len(activity_this_week)
    activity_this_week_enable: bool = activity_this_week_size < 5
    activity_this_week_data: list = []
    if activity_this_week_size > 0:
        activity_this_week_data = [dict(row)['activity'] for row in activity_this_week]
    return render_template('wsr_create.html', project_list =project_list, week_list = week_list, selected_project = project_select, selected_week = week_select, activity_this_week_enable = activity_this_week_enable, activity_this_week_data=activity_this_week_data)

@app.route('/save_data', methods=['POST'])
def save_data() -> str:
    if request.method == 'POST':
        project = request.json['project']
        week = request.json['week']
        print(request.json)
        def save_to_table(table_name, data):
            project = request.json['project']
            week = request.json['week']
            if data:
                data_to_save = [(project, week) + tuple(row) for row in data]
                filtered_data = [tup for tup in data_to_save if any(tup[:2]) and any(tup[2:])]
                print(filtered_data)
                db_helper.save_data(table_name, db_helper.get_table_dict()[table_name],filtered_data)

        save_to_table('utilization_by_task', request.json['utilization_by_task'])
        save_to_table('utilization_by_resource', request.json['utilization_by_resource'])
        save_to_table('task_last_week', request.json['task_last_week'])
        save_to_table('task_current_week', request.json['task_current_week'])
        save_to_table('week_defect_summary', request.json['week_defect_summary'])
        save_to_table('activity_this_week', request.json['activity_this_week'])

        return 'Data saved successfully'

@app.route('/edit', methods=['GET', 'POST'])
def edit() -> str:
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

    if request.method == "POST" and "select_week" in request.form:
        week_select = request.form.get("select_week")
        session["select_week"] = week_select
        project_select:str = session["select_project"]
         
    print(f"Project : {project_select} Week : {week_select}")
    utilization_by_task = db_helper.fetch_all('SELECT id, task_name, hours FROM utilization_by_task WHERE project = ? AND week = ?', (project_select, week_select))
    activity_this_week = db_helper.fetch_all('SELECT id, activity, count FROM activity_this_week WHERE project = ? AND week = ?', (project_select, week_select))
  
    return render_template('index2.html', utilization_by_task=utilization_by_task, activity_this_week=activity_this_week, project_list =project_list, week_list = week_list, selected_project = project_select, selected_week = week_select)

@app.route('/update/<table_name>', methods=['GET', 'POST'])
def update(table_name: str) -> Response | None:
    if request.method == 'POST'and 'data' in request.json:
            updated_data = request.json['data']
            for row in updated_data:
                set_clause: list = []
                values: list = []
                for key in row.keys():
                    if key != 'id':
                        set_clause.append(f"{key} = ?")
                        values.append(row[key])
                where_clause: str = f"WHERE id = ?"
                values.append(row['id'])
                set_clause_str: str = ", ".join(set_clause)
                update_string: str = f"UPDATE {table_name} SET {set_clause_str} {where_clause}"
                values_tuple = tuple(values)
                print(f"{update_string}, {values_tuple}")
                db_helper.execute_query(f"{update_string}", values_tuple)
            return jsonify({'message': 'Data updated successfully'})

@app.route('/delete/<table_name>/<int:id>', methods=['POST'])
def delete(table_name: str, id):
    db_helper.execute_query(f'DELETE FROM {table_name} WHERE id = ?', (id,))
    return jsonify({'message': 'Success'})

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=6967, threaded=True)
