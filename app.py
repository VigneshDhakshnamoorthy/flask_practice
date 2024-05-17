from typing import Any, Generator, List, Tuple
from flask import Flask, Response, jsonify, render_template, request, session
from database_helper import DatabaseHelper

app = Flask(__name__)
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'

db_name = './database/wsr.db'

db_helper = DatabaseHelper(db_name)


@app.route('/')
def index() -> str:
    return render_template('index.html')

@app.route('/edit')
def edit() -> str:
    return render_template('edit.html')

data = [
    ["John", "Doe", 30],
    ["Jane", "Smith", 25],
    ["Bob", "Johnson", 35]
]

@app.route('/editable', methods=['GET', 'POST'])
def editable():
    if request.method == 'POST':
        # Handle update request
        updated_data = request.json['data']
        for row in updated_data:
            row_index = int(row['row'])
            column_index = int(row['column'])
            new_value = row['value']
            print(new_value)
            data[row_index][column_index] = new_value
        return jsonify({'message': 'Data updated successfully'})
    # Pass data to the template
    return render_template('editable.html', data=data)

@app.route('/sample' , methods=['GET', 'POST'])
def sample() -> str:
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
    return render_template('sample.html',project_list =project_list, week_list = week_list, selected_project = project_select, selected_week = week_select)

@app.route('/save_data', methods=['POST'])
def save_data() -> str:
    if request.method == 'POST':
        project = request.json['project']
        week = request.json['week']
        print(request.json)
        def save_to_table(table_name, data):
            project = request.json['project']
            week = request.json['week']
            data_to_save = [(project, week) + tuple(row) for row in data]
            db_helper.save_data(table_name, db_helper.get_table_dict()[table_name],data_to_save)

        save_to_table('utilization_by_task', request.json['utilization_by_task'])
        save_to_table('utilization_by_resource', request.json['utilization_by_resource'])
        save_to_table('task_last_week', request.json['task_last_week'])
        save_to_table('task_current_week', request.json['task_current_week'])
        save_to_table('week_defect_summary', request.json['week_defect_summary'])
        save_to_table('activity_this_week', request.json['activity_this_week'])

        return 'Data saved successfully'

@app.route('/fetch_data', methods=['POST'])
def fetch_data() -> Response:
    project: Any = request.json['project']
    week: Any = request.json['week']
    data: dict = {}
    for table_name in db_helper.get_table_names():
        fetch_data_query: List[Tuple[Any]] = db_helper.fetch_data(table_name, 'project=? AND week=?', (project, week))
        data[table_name] = [sq for sq in fetch_data_query]
    return jsonify(data)



@app.route('/update_data', methods=['POST'])
def update_data() -> str:
    project: Any = request.json['project']
    week: Any = request.json['week']
    print(request.json)
    def update_table(table_name, data):
        for row in data:
            if 'id' in row:
                id = row.pop('id')
                set_clause = ', '.join([f"{key}=?" for key in row.keys()])
                db_helper.update_data(table_name, set_clause, 'id=?', tuple(row.values()) + (id,))
            
    update_table('utilization_by_task', request.json['utilization_by_task'])
    update_table('utilization_by_resource', request.json['utilization_by_resource'])
    update_table('task_last_week', request.json['task_last_week'])
    update_table('task_current_week', request.json['task_current_week'])
    update_table('week_defect_summary', request.json['week_defect_summary'])
    update_table('activity_this_week', request.json['activity_this_week'])

    return 'Data updated successfully'

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=6968, threaded=True)
